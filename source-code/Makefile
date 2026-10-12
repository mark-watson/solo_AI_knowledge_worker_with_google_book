PYTHON_VERSION ?= 3.14
PROJECTS := 1_start_with_auth_and_setup 2_thinking 3_images_and_text \
	5_knowledgegraphs 9_optional_google_apps a_google_adk_example

.PHONY: clean verify sync

clean:
	rm -r -f */*~ */#*
	rm -r -f */venv */*/venv
	rm -r -f */__pycache__ */*/__pycache__
	rm -r -f */.venv

# Create or refresh the virtual environment of every project.
sync:
	@for d in $(PROJECTS); do \
		printf '\n=== %s\n' "$$d"; \
		(cd "$$d" && uv sync --python $(PYTHON_VERSION)) || exit 1; \
	done

# Smoke test every project. Checks that every example imports and that the
# third-party APIs it uses still exist. Set LIVE=1 to also run the examples
# that can run unattended, which requires GOOGLE_API_KEY.
verify:
	@for d in $(PROJECTS); do \
		printf '\n=== %s\n' "$$d"; \
		(cd "$$d" && uv run --no-sync --python $(PYTHON_VERSION) \
			python ../scripts/verify_examples.py) || exit 1; \
	done
	@printf '\nAll example projects verified.\n'
