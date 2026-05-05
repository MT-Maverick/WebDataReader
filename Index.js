const express = require("express");
const multer = require("multer");
const uuid = require("uuid");
const path = require("path");
const fs = require("fs");
const app = express();

const uploadsDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadsDir);
  },
  filename: function (req, file, cb) {
    cb(null, `${uuid.v4()}-${file.originalname}`);
  },
});
const upload = multer({ storage });

const getUploadedFiles = () => {
  return fs.readdirSync(uploadsDir)
    .filter((name) => fs.lstatSync(path.join(uploadsDir, name)).isFile())
    .map((filename) => {
      const separatorIndex = filename.indexOf("-", 36);
      const name = separatorIndex !== -1 ? filename.slice(separatorIndex + 1) : filename;
      return { id: filename, name };
    });
};

let files = getUploadedFiles();

app.use(express.static(__dirname));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "Index.html"));
});

app.post("/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file selected for upload." });
  }

  files.push({ id: req.file.filename, name: req.file.originalname });
  res.json(files);
});

app.get("/files", (req, res) => {
  res.json(files);
});

app.delete("/files/:id", (req, res) => {
  const fileIndex = files.findIndex((file) => file.id === req.params.id);
  if (fileIndex === -1) {
    return res.status(404).json({ error: "File not found." });
  }

  const [removedFile] = files.splice(fileIndex, 1);
  fs.unlink(path.join(uploadsDir, removedFile.id), (err) => {
    if (err && err.code !== "ENOENT") {
      console.error("Failed to delete file:", err);
    }
  });

  res.json(files);
});

app.get("/download/:id", (req, res) => {
  const file = files.find((file) => file.id === req.params.id);
  if (file) {
    res.download(path.join(uploadsDir, file.id), file.name);
  } else {
    res.status(404).send("File not found");
  }
});

app.listen(3000, () => {
  console.log("Server is listening on port 3000");
});
