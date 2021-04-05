import React, { useState, useEffect } from "react";

const Pageinition = (props) => {
  const [currentPage, updatePage] = useState(0);

  useEffect(() => {}, [props.currentPage]);

  useEffect(() => {
    if (currentPage != props.page) {
      props.loadPage(currentPage);
    }
  }, [currentPage]);

  return (
    <nav class="pagination" role="navigation" aria-label="pagination">
      {props.showPrevNext ? (
        <>
          <a class="pagination-previous">Previous</a>
          <a class="pagination-next">Next page</a>
        </>
      ) : null}

      <ul class="pagination-list">
        {currentPage > 2 ? (
          <li>
            <a class="pagination-link" aria-label="Goto page 1">
              1
            </a>
          </li>
        ) : null}
        {currentPage > 3 ? (
          <li>
            <span class="pagination-ellipsis">&hellip;</span>
          </li>
        ) : null}

        <li>
          <a
            onClick={() => updatePage(currentPage - 1)}
            class="pagination-link"
            aria-label={`Goto page ${currentPage - 1}`}
          >
            {currentPage - 1}
          </a>
        </li>
        <li>
          <a
            onClick={() => updatePage(currentPage)}
            class="pagination-link is-current"
            aria-label={`Goto page ${currentPage}`}
          >
            {currentPage}
          </a>
        </li>
        <li>
          <a
            onClick={() => updatePage(currentPage + 1)}
            class="pagination-link"
            aria-label={`Goto page ${currentPage + 1}`}
          >
            {currentPage + 1}
          </a>
        </li>
        {currentPage + 2 < props.pageCount ? (
          <li>
            <span class="pagination-ellipsis">&hellip;</span>
          </li>
        ) : null}
        {currentPage + 1 < props.pageCount ? (
          <li>
            <a
              class="pagination-link"
              aria-label={`Goto page ${props.pageCount}`}
            >
              {props.pageCount}
            </a>
          </li>
        ) : null}
      </ul>
    </nav>
  );
};

export default Pageinition;
