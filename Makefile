CARD = uv run --project card profile-card

.PHONY: assets test check

assets:
	$(CARD) assets --spec card/card.toml --fonts card/fonts --out assets

test:
	uv run --directory card pytest -q

check: test
	$(CARD) assets --spec card/card.toml --fonts card/fonts --out build/check
	diff -r assets build/check
