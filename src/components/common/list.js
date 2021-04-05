import React from "react";
import Pageinition from "./paginition";

const ListView = (props) => {
  const { data, paginition, componentProps } = props;
  const Component = props.component;
  return (
    <>
      <div className="columns">
        {data.results.map((item) => (
          <Component item={item} {...componentProps} />
        ))}
      </div>
      {paginition ? <Pageinition page={data.page} total={data.total} /> : null}
    </>
  );
};

export default ListView;
