local Pipeline(name, image) = {
  kind: "pipeline",
  name: name,
  steps: [
    {
      name: "test",
      image: image,
      commands: [
        "pip install -U pip",
        "pip install -r requirements.txt",
        "pip install pytest",
        "pytest"
      ]
    }
  ]
};

[
  Pipeline("python-3-4", "python:3.4"),
  Pipeline("python-3-5", "python:3.5"),
  Pipeline("python-3-6", "python:3.6"),
  Pipeline("python-3-7", "python:3.7"),
  Pipeline("python-3-8", "python:3.8"),
  Pipeline("python-3-9", "python:3.9"),
]
