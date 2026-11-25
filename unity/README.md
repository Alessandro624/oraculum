# Oraculum for the Unity Editor

This guide covers the Oracle NPC in Play Mode for 2D and 3D projects. For the Python library and its API, see the [main Oraculum README](../README.md).

1. Get a complete copy of the repository. It includes bridges for Windows x64 and Linux x64. On Linux, if the bridge lacks execute permission, run `chmod +x unity/com.oraculum.npc/Tools~/Linux/oraculum-bridge` from the repository root.
2. Set up your provider. For Ollama, start the service and choose an installed model. For OpenAI, Anthropic, or OpenRouter, save your API key in a personal environment variable such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENROUTER_API_KEY`. Start Unity Hub and the Editor from an environment that has access to that variable.
3. In Unity 2021.3 or later, open **Window -> Package Manager -> + -> Add package from disk** and select `unity/com.oraculum.npc/package.json`. Keep the package folder in that location.
4. Open **Oraculum -> Local Settings**, choose your provider, and enter the exact model name. For a cloud provider, enter the name of your API key environment variable. For a local Ollama instance, you can leave the base URL blank. Click **Test Connection** to send a sample question and see the reply. Unity saves these settings in your personal Editor preferences. Restart Play Mode after changing them.
5. Drag **OracleNPC** from **Packages -> Oraculum NPC -> Prefabs** into your scene. To try the demo, import **First Consultation** from the package's **Samples** section and open the imported scene.
6. Enter **Play Mode**, click **Talk to the Oracle**, type a question, adjust **Reverence**, and click **Ask**.

The same normalized question produces the same formula. Reverence changes the invocation sent with that formula. The question itself stays on your computer. To supply your own formula from C# in Play Mode, call `await npc.AskFormula("x1 OR x2", 8)`.

## Rebuilding the bridges

On each target x64 system, activate a dedicated Python environment at the repository root and run:

```sh
python -m pip install ".[all]" pyinstaller
python unity/build_bridge.py
python unity/smoke_bridge.py
```

The smoke test runs the packaged executable against a simulated HTTP provider on localhost. The Linux executable was built on Ubuntu 24.04. Distributions with older system libraries may require a local build.
