#if UNITY_EDITOR
using System;
using UnityEditor;
using UnityEngine;

namespace Oraculum.Unity
{
    [Serializable]
    internal class OracleSettings
    {
        public string provider = "ollama", model = "", url = "", variable = "";
        private const string Key = "com.oraculum.npc.settings.v1";
        public static OracleSettings Load() => EditorPrefs.HasKey(Key)
            ? JsonUtility.FromJson<OracleSettings>(EditorPrefs.GetString(Key))
            : new OracleSettings();
        public void Save() => EditorPrefs.SetString(Key, JsonUtility.ToJson(this));
    }

    internal class OracleSettingsWindow : EditorWindow
    {
        private static readonly string[] Providers = {"ollama", "openai", "anthropic", "openrouter"};
        private OracleSettings settings;
        private OracleBridge test;
        private string status;
        [MenuItem("Oraculum/Local Settings")]
        static void Open() => GetWindow<OracleSettingsWindow>("Oraculum");
        void OnEnable() => settings = OracleSettings.Load();
        void OnDisable() => test?.Dispose();

        void OnGUI()
        {
            EditorGUI.BeginChangeCheck();
            int index = Mathf.Max(0, Array.IndexOf(Providers, settings.provider));
            string provider = Providers[EditorGUILayout.Popup("Provider", index, Providers)];
            if (provider != settings.provider) {
                settings.provider = provider;
                settings.variable = provider.ToUpperInvariant() + "_API_KEY";
                settings.url = settings.model = "";
            }
            settings.model = EditorGUILayout.TextField("Model", settings.model);
            if (provider != "anthropic")
                settings.url = EditorGUILayout.TextField("Base URL (optional)", settings.url);
            if (provider != "ollama")
                settings.variable = EditorGUILayout.TextField("API key environment variable", settings.variable);
            if (EditorGUI.EndChangeCheck()) settings.Save();
            using (new EditorGUI.DisabledScope(test != null || string.IsNullOrWhiteSpace(settings.model)))
                if (GUILayout.Button("Test Connection")) Probe();
            EditorGUILayout.HelpBox(status ?? "These settings apply to your account. Restart Play Mode after making changes.", MessageType.Info);
        }

        private async void Probe()
        {
            test = new OracleBridge();
            status = "Consulting the oracle…";
            try { status = await test.Ask(new Consult { question = "Are you there?", reverence = 5 }); }
            catch (Exception e) { status = e.Message; }
            finally { test.Dispose(); test = null; if (this) Repaint(); }
        }
    }
}
#endif
