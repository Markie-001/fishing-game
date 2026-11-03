using UnityEngine;

[RequireComponent(typeof(MeshFilter))]
[RequireComponent(typeof(MeshRenderer))]
public class WaterManager: MonoBehaviour
{
    private MeshFilter meshFilter;
    private void Awake()
    {
        meshFilter = GetComponent<MeshFilter>();
        MakeFlatShaded();
    }
    private void MakeFlatShaded()
    {
        Mesh mesh = meshFilter.mesh;
        Vector3[] oldVertices = mesh.vertices;
        int[] triangles = mesh.triangles;

        Vector3[] newVertices = new Vector3[triangles.Length];
        for (int i = 0; i < triangles.Length; i++)
        {
            newVertices[i] = oldVertices[triangles[i]];
            triangles[i] = i;
        }
        mesh.Clear();
        mesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
        mesh.vertices = newVertices;
        mesh.triangles = triangles;
        mesh.RecalculateNormals();
    }
    private void Update()
    {
        Vector3[] vertices = meshFilter.mesh.vertices;
        for (int i = 0; i < vertices.Length; i++)
        {
            Vector3 world = transform.TransformPoint(vertices[i]);
            vertices[i].y = (WaterManagement.instance.GetWaveHeight(world.x, world.z) - transform.position.y) / transform.lossyScale.y;
        }
        meshFilter.mesh.vertices = vertices;
        meshFilter.mesh.RecalculateNormals();
    }
}