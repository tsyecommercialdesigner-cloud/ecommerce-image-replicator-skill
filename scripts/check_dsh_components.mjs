/** DSH native registry/MCP adapter integration; does not run a model or read Host config.
 * node scripts/check_dsh_components.mjs <installed dsh/package.json> <locked python.exe>
 * Dependencies are resolved from that installed DSH package; no install is performed.
 * Output: one JSON report, also .cache/dsh-components.json; failures exit nonzero.
 */
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {pathToFileURL, fileURLToPath} from 'node:url';
import path from 'node:path';
import * as fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [manifest, python]=process.argv.slice(2);
assert(manifest && python, 'Supply DSH package.json and locked Python executable');
const require=createRequire(path.resolve(manifest));
const load=async name=>import(pathToFileURL(require.resolve('@deepseek-ai/'+name)));
const {Context}=await load('cordis');
const skill=await load('dsh-skill');
const filesystem=await load('dsh-skill-filesystem');
const systemPrompt=await load('dsh-system-prompt');
const tools=await load('dsh-tools');
const mcp=await load('dsh-mcp-client');
const cache=path.join(root,'.cache');
await fs.mkdir(cache,{recursive:true});
const evidence=path.join(cache,'dsh-components.json');
await fs.rm(evidence,{force:true});
const temporary=await fs.mkdtemp(path.join(cache,'dsh-components-'));
const fibers=[];
let stopCanary;
try {
  const skills=path.join(temporary,'skills');
  await fs.mkdir(skills);
  await fs.cp(path.join(root,'skills/ecommerce-image-replicator'),path.join(skills,'ecommerce-image-replicator'),{recursive:true,errorOnExist:true});
  const ctx=new Context();
  fibers.push(await ctx.plugin(skill.default));
  fibers.push(await ctx.plugin(filesystem,{includeDefaultRoots:false,customSkillDirs:[skills],watch:false}));
  const catalog=await ctx.skills.snapshot({cwd:temporary});
  assert.equal(catalog.complete,true);
  assert.equal(catalog.skills.length,1);
  const entry=catalog.skills[0];
  assert.equal(entry.name,'ecommerce-image-replicator');
  assert.equal(entry.invocation.modelInvocable,true);
  assert.equal(entry.invocation.userInvocable,true);
  const loaded=await ctx.skills.get(entry.name,{cwd:temporary});
  assert(loaded.content.includes('已有任务接手'));
  assert(skill.renderSkillContent(loaded).includes('<skill_content'));
  assert.equal(await ctx.skills.get('nonexistent-skill',{cwd:temporary}),undefined);
  fibers.push(await ctx.plugin(systemPrompt.default));
  fibers.push(await ctx.plugin(tools.default,{mode:'native'}));
  fibers.push(await ctx.plugin(mcp,{serverName:'mvp_fixture',transport:'stdio',command:python,
    args:['-X','utf8','-B',path.join(root,'tests/mvp_stub.py')],cwd:temporary,
    env:{MVP_TRACE_PATH:path.join(temporary,'calls.jsonl')},failOnStartupError:true,
    reconnect:{enabled:false},toolCallTimeoutMs:10000}));
  const schemas=ctx.tools.schemas();
  assert.deepEqual(schemas.map(x=>x.name),['mcp__mvp_fixture__get_run']);
  fibers.push(await ctx.plugin(await import(pathToFileURL(path.join(root,'tests/dsh_mvp_guard.mjs')))));
  let canaryCalls=0;
  stopCanary=ctx.tools.register({...ctx.tools.get(schemas[0].name),name:'paid_canary',
    execute:async()=>{canaryCalls++;return {content:[]};}});
  const denied=await ctx.tools.execute({callId:'canary',name:'paid_canary',arguments:{run_id:'not-used'},
    signal:AbortSignal.timeout(10000)});
  assert.equal(denied.isError,true);
  assert.equal(canaryCalls,0);
  const traces=[];
  for(let repetition=1;repetition<=3;repetition++) {
    for(const valid of [true,false]) {
      const identity='run_'+(valid?'a':'b').repeat(64);
      const result=await ctx.tools.execute({callId:`fixture-${repetition}-${valid}`,name:schemas[0].name,
        arguments:{run_id:identity},signal:AbortSignal.timeout(10000)});
      assert.equal(result.isError,!valid);
      if(valid){
        const value=result.value;
        const state=value.structuredContent ?? value.structured_content ??
          JSON.parse(value.content.find(block=>block.type==='text').text);
        assert.equal(state.run_id,identity);
        assert.equal(state.jobs.length,3);
        assert.equal(state.jobs[0].review_status,'review_required');
        assert.equal(state.jobs[1].status,'unknown');
      }
      traces.push({repetition,valid,tool:schemas[0].name,isError:result.isError});
    }
  }
  const report={status:'passed',dsh_version:JSON.parse(await fs.readFile(manifest,'utf8')).version,
    skill_sha256:createHash('sha256').update(await fs.readFile(path.join(skills,entry.name,'SKILL.md'))).digest('hex'),
    source:entry.source,invocation:entry.invocation,catalog_complete:catalog.complete,traces,
    scope:'native DSH components; programmatic calls; not Desktop/headless model behavior or natural-language selection',
    provider_requests:0,model_requests:0,guard_canary_calls:canaryCalls,guard_rejected:denied.isError};
  await fs.writeFile(evidence,JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {
  stopCanary?.();
  for(const fiber of fibers.reverse()) await fiber.dispose();
  assert(path.resolve(temporary).startsWith(path.resolve(cache)+path.sep));
  await fs.rm(temporary,{recursive:true,force:true});
}
