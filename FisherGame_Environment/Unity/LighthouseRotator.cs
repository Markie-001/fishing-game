using UnityEngine;

// Turns the lighthouse beam rig (Fish_Lighthouse_BeamRig: two spot lights + two beam meshes).
// Put this on the Fish_Lighthouse_BeamRig object after importing Island_FishMarket.fbx.
// 82.5 deg/s matches the Blender driver (0.06 rad per frame at 24 fps).
public class LighthouseRotator : MonoBehaviour
{
    public float degreesPerSecond = 82.5f;

    private void Update()
    {
        transform.Rotate(Vector3.up, degreesPerSecond * Time.deltaTime, Space.World);
    }
}
