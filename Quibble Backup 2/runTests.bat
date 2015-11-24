setLocal EnableDelayedExpansion
echo. > expectedOutputs.txt
echo. > outputs.txt

for /d %%i in (tests\*) do (
	for /d %%j in (%%i\*) do (
		type %%j\input\input.txt | python.exe frontEnd.py %%j\input\currentEvents.txt %%j\eventTransaction.txt > %%j\output.txt
		type %%j\eventTransaction.txt >> eventTransactions.txt
		type %%j\eventTransactionExpected.txt >> eventTransactionsExpected.txt
	)
)

pause

FC eventTransactions.txt eventTransactionsExpected.txt

pause