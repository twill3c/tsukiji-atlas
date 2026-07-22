# パイプライン実行入口(GUIDE §6)。bronze は実ネットワークを叩く唯一の経路(手動実行のみ)
.PHONY: bronze silver gold test

bronze:
	python -m extract.run_bronze

silver:
	python -m transform.run_silver

gold:
	python -m gold.run_gold

test:
	python -m pytest -q --tb=no
