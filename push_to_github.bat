@echo off
echo ================================================================================
echo                    PUSHING TO GITHUB
echo ================================================================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    echo.
)

REM Add all files
echo Adding files...
git add .
echo.

REM Show status
echo Files to be committed:
git status --short
echo.

REM Prompt for commit message
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update: ESG Portfolio Optimizer

REM Commit
echo Committing with message: %commit_msg%
git commit -m "%commit_msg%"
echo.

REM Check if remote exists
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo FIRST TIME SETUP
    echo ================================================================================
    echo.
    echo Please enter your GitHub repository URL
    echo Example: https://github.com/yourusername/esg-portfolio-optimizer.git
    echo.
    set /p repo_url="GitHub URL: "
    
    echo Adding remote origin...
    git remote add origin %repo_url%
    echo.
    
    echo Setting main branch...
    git branch -M main
    echo.
)

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main
echo.

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo PUSH FAILED
    echo ================================================================================
    echo.
    echo If this is your first push, you may need to:
    echo 1. Create the repository on GitHub first
    echo 2. Set up authentication (personal access token or SSH key)
    echo.
    echo Try running these commands manually:
    echo   git remote add origin YOUR_GITHUB_URL
    echo   git branch -M main
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ================================================================================
    echo SUCCESS!
    echo ================================================================================
    echo.
    echo Your code has been pushed to GitHub!
    echo.
    echo Next steps:
    echo 1. Go to your GitHub repository
    echo 2. Add topics/tags: machine-learning, quantitative-finance, esg-investing
    echo 3. Add to your resume!
    echo.
)

pause
