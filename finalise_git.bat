@echo off
REM Run this from the project root on your Windows machine.
REM It clears any stale lock, sets identity, creates the feature branch,
REM commits the changes in small steps, merges back into main, and pushes.

if exist ".git\index.lock" del /f ".git\index.lock"

git config user.email "faisal.durran@gmail.com"
git config user.name "drcoolio666"

git checkout -b feature_carpark_logic

git add smartpark/car.py smartpark/carpark.py smartpark/config.json
git commit -m "Add Car and CarPark classes with json config loader and activity log"

git add smartpark/config_parser.py smartpark/no_pi.py smartpark/mocks.py
git commit -m "Wire no_pi launcher to the real CarPark manager and tidy parser"

git add tests/carpark_test.py tests/test_config.py
git commit -m "Add unit tests for config parsing, entry exit counts and edge cases"

git add README.md checklist.md
git commit -m "Update README and checklist to reflect the completed project"

git checkout main
git merge --no-ff feature_carpark_logic -m "Merge branch 'feature_carpark_logic' into main"

git push origin main
git push origin feature_carpark_logic

echo.
echo Done. Verify with: git log --oneline -10
