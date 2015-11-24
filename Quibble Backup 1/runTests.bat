setLocal EnableDelayedExpansion

for /d %%i in (tests\*) do (
	for /d %%j in (%%i\*) do (
		echo %%j
	)
)
type commands.txt | python.exe frontEnd.py currentEvents.txt eventTransaction.txt > output.txt

pause