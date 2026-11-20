import json, pathlib, re
root = pathlib.Path(__file__).parent
source=(root/'Test-CoModelFabricX2R0.ps1').read_text()
obj=json.loads((root/'CoWorkObject_R0_example.json').read_text())
checks={
 'mode_explicit':"[ValidateSet('Check','SelfTest','OpenClaude','OpenOrbSource')]" in source,
 'default_readonly':"[string]$Mode = 'Check'" in source,
 'probe_loopback_only':"http://127.0.0.1:11434/api/tags" in source,
 'probe_timeout':"-TimeoutSec 2" in source,
 'skip_support':"[switch]$SkipOllama" in source,
 'no_env_credential_access':not re.search(r'(?i)(\$env:|get-credential|convertto-securestring|read-host|secretmanagement|vault)',source),
 'no_clipboard_or_input_capture':not re.search(r'(?i)(get-clipboard|set-clipboard|add-type|registerhotkey|setwindowshookex|sendkeys)',source),
 'no_file_write':not re.search(r'(?i)(out-file|set-content|add-content|new-item|remove-item|export-|redirection\s*>)',source),
 'no_scheduled_tasks':not re.search(r'(?i)(register-scheduledtask|schtasks|start-job|register-objectevent)',source),
 'claude_user_owned':"user_owned_account=$true" in source,
 'no_login_assertion':"AUTH_UNKNOWN_NOT_PROBED" in source,
 'no_implicit_browser_start':"'OpenClaude' {" in source and "'OpenOrbSource' {" in source,
 'no_external_api_calls':source.count('Invoke-RestMethod')==1,
 'full_task_public_only':obj['confidentiality']=='PUBLIC_SAFE_FIXTURE_ONLY',
 'task_no_effects':obj['authority']=='NONE_ANALYSIS_ONLY',
 'no_budget_spend':obj['resource_policy']['max_automatic_spend_usd']==0,
 'bounded_workers':obj['resource_policy']['max_active_workers']<=2,
 'no_source_sha_pretence':obj['source_sha']=='NOT_PINNED_UNTIL_ACTUAL_RUN',
 'no_fake_receiver_ack':obj['receiver_ack'] is None,
 'no_dispatch_claim':obj['dispatch_state'].startswith('HELD_'),
 'no_account_role_equality': 'ROLE_NE_EXTERNAL_ACCOUNT' in obj['nonclaims'],
 'selftest_cases':len(re.findall(r"^\s*\@\{name='",source,re.M))==12,
 'philosophy_outside_adapter': not re.search(r'(?i)(G_d|extraterrestrial|ET_contact)',source)
}
print(json.dumps({'checks':checks,'pass':sum(checks.values()),'total':len(checks),'status':'PASS' if all(checks.values()) else 'FAIL'},indent=2))
assert all(checks.values())
