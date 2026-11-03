using UnityEngine;

public class Draaien : MonoBehaviour
{
    [SerializeField ]private float snelHeid = 100f;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        Debug.Log("Hoi");
    }

    // Update is called once per frame
    void Update()
    {
        spinMe(snelHeid);
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.tag == "kill" && other.gameObject != null)
        {
            Destroy(gameObject);
        }
    }

    void spinMe(float spinsSpeed)
    {
        transform.Rotate(new Vector3(0, spinsSpeed * Time.deltaTime, 0));
    }
}
