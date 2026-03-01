.PHONY: doctor validate compile compile-fast

doctor:
	python scripts_doctor.py

validate:
	python mcp_enterprise_compiler.py --validate-env

compile:
	python mcp_enterprise_compiler.py

compile-fast:
	python mcp_enterprise_compiler.py --skip-install
