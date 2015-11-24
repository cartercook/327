rem tests are stored in folders named after the command they test.
rem frontEnd.py outputs an eventTransaction.txt and output.txt file
rem into each test's folder. thsese eventTransaction.txt's are then fc'd
rem against each test's eventTransactionExpected.txt, and unexpected
rem differences between them are appended to differences.txt.

setLocal EnableDelayedExpansion
echo. > differences.txt

for /d %%i in (tests\*) do (
	for /d %%j in (%%i\*) do (
		type "%%j\input\input.txt" | python.exe frontEnd.py "%%j\input\currentEvents.txt" "%%j\eventTransaction.txt" > "%%j\output.txt"
		fc "%%j\eventTransaction.txt" "%%j\eventTransactionExpected.txt"
		if errorlevel 2 (
			fc "%%j\eventTransaction.txt" "%%j\eventTransactionExpected.txt" >> differences.txt
		)
	)
)

pause