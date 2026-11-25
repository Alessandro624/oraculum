using System;
using System.Threading.Tasks;
using UnityEngine;

namespace Oraculum.Unity
{
    public sealed class OracleNPC : MonoBehaviour
    {
        [Range(1, 10)] public int reverence = 5;
#if UNITY_EDITOR
        private OracleBridge bridge;
        private string question = "", message = "";
        private bool open, waiting;

        void OnEnable() => bridge = new OracleBridge();
        void OnDisable() { bridge?.Dispose(); bridge = null; waiting = false; }

        public Task<string> AskQuestion(string question, int reverenceLevel) =>
            bridge.Ask(new Consult { question = question, reverence = reverenceLevel });
        public Task<string> AskFormula(string formula, int reverenceLevel) =>
            bridge.Ask(new Consult { formula = formula, reverence = reverenceLevel });

        void OnGUI()
        {
            GUILayout.BeginArea(new Rect(12, 12, Mathf.Min(420, Screen.width - 24), Screen.height - 24));
            if (!open) { if (GUILayout.Button("Talk to the Oracle")) open = true; }
            else {
                GUILayout.Label("What is your question?");
                question = GUILayout.TextField(question, 512);
                GUILayout.Label("Reverence: " + reverence);
                reverence = Mathf.RoundToInt(GUILayout.HorizontalSlider(reverence, 1, 10));
                bool previous = GUI.enabled;
                GUI.enabled = previous && !waiting && !string.IsNullOrWhiteSpace(question);
                if (GUILayout.Button("Ask")) Speak();
                GUI.enabled = previous;
                GUILayout.Label(message);
                if (GUILayout.Button("Close")) open = false;
            }
            GUILayout.EndArea();
        }

        private async void Speak()
        {
            var session = bridge;
            waiting = true;
            message = "The oracle is pondering…";
            try {
                var comment = await AskQuestion(question, reverence);
                if (session == bridge) message = comment;
            }
            catch (Exception e) { if (session == bridge) message = e.Message; }
            finally { if (session == bridge) waiting = false; }
        }
#endif
    }
}
