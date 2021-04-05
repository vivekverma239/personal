import React, { useState } from "react";
import { Editor } from "@tinymce/tinymce-react";
import MDEditor from "@uiw/react-md-editor";
import { Radio } from "antd";

// const renderers = {
//   code: ({ children, language, value }) => {
//     if (language.toLocaleLowerCase() === "mermaid") {
//       const Elm = document.createElement("div");
//       Elm.id = "demo";
//       const svg = mermaid.render("demo", value);
//       return (
//         <pre>
//           <code dangerouslySetInnerHTML={{ __html: svg }} />
//         </pre>
//       );
//     }
//     return children;
//   },
// };

export default function MarkdownEditor(props) {
  const [preview, updatePreview] = useState("preview");

  return (
    <div>
      <Radio.Group
        size="small"
        onChange={updatePreview}
        value={preview}
        style={{ marginBottom: "10px" }}
      >
        <Radio.Button value="preview">Preview</Radio.Button>
        <Radio.Button value="edit">Edit</Radio.Button>
      </Radio.Group>
      <MDEditor
        height={"80vh"}
        value={props.value || ""}
        // previewOptions={{ renderers: renderers }}
        preview={preview}
      />
    </div>
  );
}
// class MarkdownEditor extends React.Component {
//   handleEditorChange = (e) => {
//     console.log("Content was updated:", e.target.getContent());
//   };

//   render() {
//     return (
//       <Editor
//         apiKey="rj6shd2utduli5t677q2bkdojs62mqpp8u1jzhy86lsrb1tk"
//         initialValue="<p>Initial content</p>"
//         init={{
//           height: 500,
//           menubar: false,
//           plugins: [
//             "advlist autolink lists link image",
//             "charmap print preview anchor help",
//             "searchreplace visualblocks code",
//             "insertdatetime media table paste wordcount",
//           ],
//           toolbar:
//             "undo redo | formatselect | bold italic | \
//             alignleft aligncenter alignright | \
//             bullist numlist outdent indent | help",
//         }}
//         onChange={this.handleEditorChange}
//       />
//     );
//   }
// }

// export default App;
