"""server_load: the structure loads on a real 26.3 server (place template succeeds, no log errors) and a
deterministic sample of blocks reads back exactly (execute if block). Needs a running server (report.py)."""
NAME = "server_load"
DESCRIPTION = "Template places on the 26.3 test server and sampled blocks read back."
DEFAULTS = {}
NEEDS_SERVER = True


def validate(ctx):
    return ctx.server.check_map(ctx.result, ctx.config)
