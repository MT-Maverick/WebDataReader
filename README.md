# fileSharingApp
A web based file sharing  app
That will allow devices to share files through a 
Peer to peer network 

## Quick start

Run both the Node upload service and Streamlit dashboard with one command:

```bash
cd "C:\Users\MfundoSindane\Desktop\fileSharingApp-main"
npm start
```

This starts:
- Node.js upload server at `http://localhost:3000`
- Streamlit dashboard at `http://localhost:8501`

Both services run concurrently and will be available in your browser.

## Manual setup (alternative)

### Run the Node upload service

```bash
cd "C:\Users\MfundoSindane\Desktop\fileSharingApp-main"
npm run server
```

### Run the Streamlit dashboard

```bash
cd "C:\Users\MfundoSindane\Desktop\fileSharingApp-main"
python -m pip install -r python/requirements.txt
npm run dashboard
```

## Python Streamlit Dashboard

This project supports a Python Streamlit dashboard that reads uploaded spreadsheet files from the shared `uploads/` folder.

### Hosting behind IIS

To make the dashboard available through IIS, use IIS Application Request Routing (ARR) or a reverse proxy to forward requests from IIS to `http://localhost:8501` for Streamlit and `http://localhost:3000` for the upload service.
