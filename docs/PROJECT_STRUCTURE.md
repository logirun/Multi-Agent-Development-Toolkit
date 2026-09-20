# AegisFlow Codebase Architecture Map (Repo Map)
# Generated via AST Analysis | Root: 多Agent开发工具

## /src
- `src\auth.py`:
    • class AuthService(__init__, generate_token, verify_token, authenticate)

## /tools
- `tools\board_renderer.py`:
    • def format_stage_badge(stage)
    • def format_priority_badge(priority)
    • class BoardRenderer(render_board)
- `tools\gatekeeper.py`:
    • class Gatekeeper(__init__, hash_file, fast_lint, check_role_permission, check_gate_1_contract...)
- `tools\git_hook.py`:
    • class GitHookManager(__init__, install_hook, uninstall_hook, verify_pre_commit)
- `tools\heartbeat.py`:
    • class StudioHeartbeat(__init__, run_inspection, print_heartbeat_report)
- `tools\kanban_server.py`:
    • class KanbanHandler(log_message, do_GET)
    • def run_server(port)
- `tools\repo_hygiene.py`:
    • class RepoHygieneGuard(__init__, check_root_cleanliness, check_test_mirror_consistency, check_directory_depth, generate_repo_map...)
- `tools\stack_sniffer.py`:
    • class StackSniffer(__init__, sniff, save_profile)
- `tools\state_manager.py`:
    • class StateManager(__init__, _load, _save, _log_event, _record_checkpoint...)
- `tools\vc_cli.py`:
    • def main()
