# Delphi Software Bot (Streamlit Demo Application)
![image](https://github.com/user-attachments/assets/1b6bc740-a090-4d8a-986c-d51705d26384)

This project is a demo application built with Streamlit and LangChain. It serves as a conversational assistant, leveraging AWS Bedrock and other tools to retrieve and process knowledge base information. The app is designed to answer user queries based on contextual knowledge from a defined knowledge base.

## Features
- Conversational interface powered by Streamlit.
- Integration with AWS services for knowledge retrieval.
- Context-aware answers using LangChain.
- Persistent memory for chat history.

---

## Deployment Instructions

### Prerequisites
Ensure the following are installed on your local machine or server:
1. Python 3.9 or newer
2. AWS CLI configured with valid credentials
3. `git` for version control

### Deployment on AWS EC2

#### Step 1: Launch an EC2 Instance
1. Log in to your AWS Management Console.
2. Launch an EC2 instance using the **Ubuntu 22.04** AMI.
3. Attach a security group that allows inbound traffic on ports **22** (SSH) and **8501** (Streamlit).

#### Step 2: SSH into the Instance
```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

#### Step 3: Install Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

#### Step 4: Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo>.git streamlit_demo
cd streamlit_demo
```

#### Step 5: Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Run the Application
```bash
streamlit run langchain-kb.py --server.port 8501 --server.enableCORS false --server.headless true
```

#### Step 7: Keep the Application Running
Use one of the following tools to ensure the app continues running:
- **systemd**:
  - Create a service file:
    ```bash
    sudo nano /etc/systemd/system/streamlit.service
    ```
    Add the following content:
    ```
    [Unit]
    Description=Streamlit Service
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/streamlit_demo
    ExecStart=/home/ubuntu/streamlit_demo/venv/bin/streamlit run langchain-kb.py --server.port 8501 --server.enableCORS false --server.headless true
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
  - Start and enable the service:
    ```bash
    sudo systemctl start streamlit
    sudo systemctl enable streamlit
    ```

- **screen**:
  ```bash
  screen -S streamlit
  streamlit run langchain-kb.py --server.port 8501 --server.enableCORS false --server.headless true
  ```
  Press `Ctrl+A` then `D` to detach.

- **tmux**:
  ```bash
  tmux new -s streamlit
  streamlit run langchain-kb.py --server.port 8501 --server.enableCORS false --server.headless true
  ```
  Press `Ctrl+B` then `D` to detach.

#### Step 8: Access the Application
Visit the following URL in your browser:
```
http://<EC2_PUBLIC_IP>:8501
```
