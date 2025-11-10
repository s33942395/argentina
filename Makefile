.PHONY: all update pdf clean rename

REPORT_MD := /workspaces/argentina/報告_阿根廷經濟改革與匯率_整合版.md
REPORT_PDF := /workspaces/argentina/報告_阿根廷經濟改革與匯率_整合版.pdf
SCRIPT := /workspaces/argentina/update_all.sh

all: update

update:
	bash $(SCRIPT)

pdf:
	pandoc "$(REPORT_MD)" -o "$(REPORT_PDF)"

clean:
	rm -f "$(REPORT_PDF)"

rename:
	cp "$(REPORT_MD)" /workspaces/argentina/report.md
	@echo "已建立 ASCII 檔名：report.md"