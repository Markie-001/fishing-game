using UnityEngine;

public class WaterManagement : MonoBehaviour
{
    public static WaterManagement instance;
    public float amplitude = 1f;
    public float length = 2f;
    public float speed = 1f;
    public float offset = 0f;
    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
        }
        else if (instance != this)
        {
            Debug.Log("Instace already exist, destroying object");
            Destroy(this);
        }
    } 
    private void Update()
    {
        offset += Time.deltaTime * speed;
    }
    public float GetWaveHeight(float _x, float _z)
    {
        return amplitude * 0.5f * (Mathf.Sin(_x / length + offset) + Mathf.Sin(_z / (length * 0.7f) + offset * 1.3f));
    }
}