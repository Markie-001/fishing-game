using System;
using UnityEngine;

public class draaien : MonoBehaviour
{
    [SerializeField] private float snelheid = 100f;
    
    void Start()
    {
        Debug.Log("Hello World");
    }

    void Update()
    {
        spinme();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.tag == "Kill" && other.gameObject)
        {
            Destroy(gameObject);
        }
    }

    void spinme()
    {
        transform.Rotate(new Vector3(0, snelheid, 0));
    }
}
