# from pathlib import Path
# from fastmcp import FastMCP
# from fastmcp.server.providers.skills import SkillsDirectoryProvider
# import mcpcat
# from mcpcat import MCPCatOptions, UserIdentity
#
# # Create MCP server
# mcp = FastMCP("Skills Server")
#
# # Add Skills Directory Provider
# mcp.add_provider(
#     SkillsDirectoryProvider(
#         # roots=Path.cwd() / "skills"  # change if needed
#         # supporting_files="template",  # default
#         # reload=True,  # enable only during development
#         roots=Path(__file__).resolve().parent / "skills"
#     )
# )
#
# # mcpcat.track(mcp, None, mcpcat.MCPCatOptions(
# #     exporters={
# #         "otlp": {
# #             "type": "otlp",
# #             "endpoint": "http://localhost:4318/v1/traces"
# #         }
# #     }
# # ))
# # def identify_user(request, extra):
# #     user = myapi.get_user(request.params.arguments.token)
# #     return UserIdentity(
# #         user_id=user.id,
# #         user_name=user.name,
# #         user_data={
# #             "favorite_color": user.favorite_color,
# #         },
# #     )
#
# def identify_user(request, context):
#     user_id = request.params.arguments.get('userId')
#     if not user_id:
#         return None
#
#     return UserIdentity(
#         user_id=user_id,
#         user_name=request.params.arguments.get('userName')
#     )
#
# mcpcat.track(mcp, "proj_3CU3xgDxBOjO9Xd0h9QPxXTRi1V", MCPCatOptions(identify=identify_user))
#
# # if __name__ == "__main__":
# #     # Run MCP server
# #     mcp.run()
# if __name__ == "__main__":
#     mcp.run()

import sys
from pathlib import Path

from fastmcp import FastMCP

from fastmcp.server.providers.skills import SkillsDirectoryProvider


# Ensure sibling modules import when cwd is not mcp_server (some MCP hosts).
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))



# Create MCP server
mcp = FastMCP(
    name="skills-server",
    version="1.0.0"
)

# Add Skills provider
mcp.add_provider(
    SkillsDirectoryProvider(
        roots=Path(__file__).resolve().parent / "skills"
    )
)
def load_combined_skill():
    base = Path(__file__).resolve().parent / "skills"

    def read_file(path):
        return path.read_text() if path.exists() else ""

    actionmeta = read_file(base / "ActionMeta" / "SKILL.md")
    actionmodel = read_file(base / "ActionModel" / "SKILL.md")
    appactionmodel = read_file(base / "AppActionModel" / "SKILL.md")
    appactionmeta = read_file(base / "AppActionMeta" / "SKILL.md")
    bestpractices = read_file(base / "GoodPractices" / "SKILL.md")

    return "\n\n".join([
        actionmeta,
        actionmodel,
        appactionmodel,
        appactionmeta,
        bestpractices
    ])
# def load_combined_skill():
#     actionmeta = read("skills/ActionMeta/SKILL.md")
#     actionmodel = read("skills/ActionModel/SKILL.md")
#     appactionmodel = read("skills/AppActionModel/SKILL.md")
#     appactionmeta = read("skills/AppActionMeta/SKILL.md")
#     bestpractices=read("skills/GoodPractices/SKILL.md")
#
#
#
#     return actionmeta + "\n\n" + actionmodel+ "\n\n"+appactionmodel+"\n\n"+appactionmeta+"\n\n"+bestpractices

# ✅ TOOL (your function)
# @mcp.tool
# def generate_action_code(spec: str) -> str:
#     """
#     Parse an ACTIONS-style plain-text spec (lines like `-- POST /widgets/create`)
#     and return Java `AppActionModel` skeletons (`_defn` + `callLogic` stubs).
#     If no `-- METHOD /path` lines are found, returns a short hint plus the raw spec.
#     """
#     return generate_java_skeletons(spec)
#
#
# @mcp.tool()
# async def generate_code(requirement: str) -> str:
#     skill = load_full_skill("code-gen")
#
#     prompt = f"{skill}\n\nUser: {requirement}"
#
#     return prompt
@mcp.tool()
async def start_generate_crud_code():
    base = Path(__file__).resolve().parent / "skills"
    def read_file(path):
        return path.read_text() if path.exists() else ""

    starter = read_file(base / "CRUD_starter" / "SKILL.md")
    return  starter


@mcp.tool()
async def generate_full_crud_code_using_skills(requirement: str) -> dict:
    skill = load_combined_skill()

    return {
        "role": "system",
        "content": skill,
        "task": requirement,
        "instruction": "Generate production-ready CRUD API"
    }

# Run server (STDIO mode for Cursor)
if __name__ == "__main__":
    mcp.run()