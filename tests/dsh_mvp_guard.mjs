/** Runtime test guard: registered tools may only load this Skill or call the offline stub. */
export const name='mvp-tool-guard';
export const inject=['tools'];
export function apply(ctx){
  ctx.tools.guard(exec=>['skill','mcp__mvp_fixture__get_run'].includes(exec.name)
    ? undefined : 'MVP evaluation permits only skill and offline fixture get_run');
}
