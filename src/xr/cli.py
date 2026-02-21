"""CLI entry point."""
import click
from xr import __version__

@click.group()
@click.version_option(__version__, prog_name="xr")
@click.option("--pretty", is_flag=True, help="Output raw JSON")
@click.option("--save", is_flag=True, help="Save output to configured directory")
@click.option("--no-cache", is_flag=True, help="Bypass cache, force fresh API call")
@click.pass_context
def main(ctx, pretty, save, no_cache):
    """XR — X (Twitter) Research CLI."""
    ctx.ensure_object(dict)
    ctx.obj["pretty"] = pretty
    ctx.obj["save"] = save
    ctx.obj["no_cache"] = no_cache
