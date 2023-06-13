using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraControl : MonoBehaviour
{
    public float rotationSpeed = 5f;
    public float movementSpeed = 2.5f;

    private bool isMouseRightButtonDown = false;

    private void Update()
    {
        // 检测鼠标右键按下状态
        if (Input.GetMouseButtonDown(1))
        {
            isMouseRightButtonDown = true;
        }
        else if (Input.GetMouseButtonUp(1))
        {
            isMouseRightButtonDown = false;
        }

        // 只有鼠标右键按下时才进行旋转
        if (isMouseRightButtonDown)
        {
            float rotationX = Input.GetAxis("Mouse X") * rotationSpeed;
            float rotationY = Input.GetAxis("Mouse Y") * rotationSpeed;

            // 绕垂直轴旋转
            transform.RotateAround(transform.position, Vector3.up, rotationX);

            // 绕水平轴旋转
            transform.RotateAround(transform.position, -transform.right, rotationY);
        }

        // 同时按下鼠标右键和键盘时才进行移动
        if (isMouseRightButtonDown && (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.S) ||
                                       Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.Q) || Input.GetKey(KeyCode.E)))
        {
            float moveVertical = Input.GetAxis("Vertical");
            float moveHorizontal = Input.GetAxis("Horizontal");
            float moveUp = Input.GetKey(KeyCode.E) ? 1f : 0f;
            float moveDown = Input.GetKey(KeyCode.Q) ? 1f : 0f;

            Vector3 movement = new Vector3(moveHorizontal, moveUp - moveDown, moveVertical);
            transform.Translate(movement * movementSpeed * Time.deltaTime, Space.Self);
        }
    }
}

