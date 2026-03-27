# Session Persisting Across Builds Investigation

## Issue Summary
You mentioned that when you build the application and run it, you automatically are logged in as `testinglogin@gmail.com`. You suspected this was a bug in the build process.

I have investigated how sessions are stored and how the build process handles files. **The build process is working correctly and is not bundling the `.session.json` file into the app.** 

What's actually happening is standard macOS application behavior:
1. When you run the frozen `.app`, it stores runtime data in `~/Library/Application Support/ScreenGaze/`.
2. Yesterday (or earlier in your testing), you ran the app and logged in as `testinglogin`. The session was saved to `~/Library/Application Support/ScreenGaze/.session.json`.
3. When you rebuild the app and run it again, macOS keeps the `Application Support` directory intact. The new build simply loads the existing session file from that directory, leading to the auto-login.

For a completely new user installing the app for the first time, this folder will be empty, and they **will** be forced to log in on first start.

## User Review Required
> [!NOTE]
> Everything is working as a desktop app should! Users naturally expect to stay logged in when an application is updated to a new version. 

How would you like to proceed?
1. **No changes needed**: The current behavior is correct for actual users. You can manually delete `~/Library/Application Support/ScreenGaze/` when you want to simulate a "first start" for your own testing.
2. **Clear session on every startup**: Change the code so the app *never* remembers user logins across app restarts.
3. **Other**: Is there a specific behavior you prefer?

Let me know!
