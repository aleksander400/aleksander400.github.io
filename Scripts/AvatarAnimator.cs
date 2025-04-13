using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class AvatarAnimator : MonoBehaviour
{
    public Image avatarImage;
    public Sprite normalAvatar;
    public Sprite talkingAvatar;
    public float animationDelay = 1f;

    private Coroutine animationRoutine;

    public void Speak(string message)
    {
        // Wyświetl wiadomość w UI
        Debug.Log("AI: " + message);
        
        // Rozpocznij animację
        if (animationRoutine != null)
        {
            StopCoroutine(animationRoutine);
        }
        animationRoutine = StartCoroutine(AnimateAvatar());
        
        // Tutaj dodaj kod syntezy mowy jeśli potrzebny
    }

    private IEnumerator AnimateAvatar()
    {
        // Włącz animację mówienia
        avatarImage.sprite = talkingAvatar;
        
        // Czekaj określony czas
        yield return new WaitForSeconds(animationDelay);
        
        // Wyłącz animację
        avatarImage.sprite = normalAvatar;
    }

    void OnDisable()
    {
        if (animationRoutine != null)
        {
            StopCoroutine(animationRoutine);
        }
    }
}
