using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

public class AIInterfaceController : MonoBehaviour
{
    public Image avatarImage;
    public Sprite normalAvatar;
    public Sprite talkingAvatar;
    public TMP_Text chatText;
    public TMP_InputField inputField;
    public ScrollRect scrollRect;
    public Button sendButton;
    public Button voiceButton;
    public Button quitButton;

    void Start()
    {
        // Setup button listeners
        sendButton.onClick.AddListener(ProcessInput);
        voiceButton.onClick.AddListener(StartVoiceInput);
        quitButton.onClick.AddListener(QuitApp);

        // Initial message
        AddMessage("System", "Witaj! Gotowy do działania.");
    }

    void ProcessInput()
    {
        string userInput = inputField.text;
        AddMessage("User", userInput);
        inputField.text = "";
        StartCoroutine(HandleCommand(userInput));
    }

    void StartVoiceInput()
    {
        StartCoroutine(VoiceInputRoutine());
    }

    IEnumerator VoiceInputRoutine()
    {
        AddMessage("System", "Słucham...");
        // Here you would integrate with your voice recognition system
        // For now simulating with a delay
        yield return new WaitForSeconds(2f);
        string voiceInput = "[Symulowana odpowiedź głosowa]";
        AddMessage("User", voiceInput);
        StartCoroutine(HandleCommand(voiceInput));
    }

    IEnumerator HandleCommand(string command)
    {
        // Here you would integrate with your command processing system
        yield return new WaitForSeconds(1f);
        
        // Simulate processing
        string response = "Symulowana odpowiedź na: " + command;
        AddMessage("AI", response);
        
        // Animate avatar while "speaking"
        yield return StartCoroutine(AnimateAvatarTalking());
    }

    IEnumerator AnimateAvatarTalking()
    {
        avatarImage.sprite = talkingAvatar;
        yield return new WaitForSeconds(2f);
        avatarImage.sprite = normalAvatar;
    }

    void AddMessage(string sender, string message)
    {
        chatText.text += $"{sender}: {message}\n";
        Canvas.ForceUpdateCanvases();
        scrollRect.verticalNormalizedPosition = 0f;
        Canvas.ForceUpdateCanvases();
    }

    void QuitApp()
    {
        Application.Quit();
    }
}
