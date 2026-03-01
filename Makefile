.PHONY: doctor validate compile compile-fast

doctor:
	python scripts_doctor.py

validate:
	python bridge/mcp_enterprise_compiler.py --validate-env

compile:
	python bridge/mcp_enterprise_compiler.py

compile-fast:
	python bridge/mcp_enterprise_compiler.py --skip-install
