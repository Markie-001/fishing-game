using UnityEngine;
using UnityEngine.InputSystem;

public class vishengel : MonoBehaviour
{
    public Rigidbody dobber;
    public Transform hengelTip;
    public float werpspeed = 6f;
    public float reelspeed = 3f;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKey(KeyCode.Mouse0))
        {
            dobber.linearVelocity = hengelTip.forward * werpspeed;
        }
    }
}
