import { h, Component, render } from 'https://cdn.skypack.dev/preact@10.4.7';
import { useEffect, useState, useRef, useMemo, useReducer } from 'https://cdn.skypack.dev/preact@10.4.7/hooks'
import { buildOptions } from "/static/js/components/util.js";

export const PaginateHandle = ({page, setPage, pageSize, url, ...props}) => {

    const [numPages, setNumPages] = useState(0)

    useEffect(() => {
        let getData = async () => {
            let response = await fetch(
                url,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                }
            )

            setNumPages(Math.ceil(response.headers.get("X-Total-Count") / pageSize))
        }
        getData()
    }, [url])

    const displayedPages = 8
    let getPageButtons = (page, numPages) => {
        if(numPages < displayedPages){
            return [...Array(numPages).keys()]
        } else if(page < displayedPages) {
            return [...Array(displayedPages).keys()]
        } else {
            return [...Array(displayedPages).keys()].map(x => x + (page - displayedPages))
        }
    }

    return (
        h("div", {className: `paginator ${props.className}`},
            h("div", {},
                ... page != 1 ? [
                    h("img", {src:"/static/images/icons/Left-Arrow-Double.svg", alt: "Double Left Arrow", onclick: () => setPage(1)}),
                    h("img", {src:"/static/images/icons/Left-Arrow.svg", alt: "Left Arrow", onclick: () => setPage(Math.max(page - 1, 1))})
                ] : [],
                getPageButtons(page, numPages).map((i) => {
                    let oneIndexedValue = i + 1
                    let buttonClass = oneIndexedValue == page ? "btn-primary" : "btn-secondary";
                    return h("button", {className: `btn p-1 px-2 me-1 ${buttonClass}`, onclick: () => setPage(oneIndexedValue)}, oneIndexedValue)
                }),
                ... page != numPages ? [
                    h("img", {src:"/static/images/icons/Right-Arrow.svg", alt: "Left Arrow", onclick: () => setPage(Math.min(page + 1, numPages))}),
                    h("img", {src:"/static/images/icons/Right-Arrow-Double.svg", alt: "Double Left Arrow", onclick: () => setPage(numPages)}),
                ] : [],
            )
        )
    )
}

export const QueryHandle = ({setQuery, ...props}) => {

    let inputTimeoutID = undefined;
    let setQueryWrapper = (q) => {
        let f = () => {
            if(q){
                setQuery(`name%3D~${q}`);
            } else {
                setQuery("");
            }

        }

        clearTimeout(inputTimeoutID)
        inputTimeoutID = setTimeout(f, 500, q)
    }

    return (
        h("div", {...props},
            h("input", {oninput: (e) => setQueryWrapper(e.target.value), type:"text", class:"form-control", id:"query", placeholder: "Search"}),
        )
    )
}

export const SortHandle = ({options, setSort, ...props}) => {

    return (
        h("div", {...props},
            h("select", {className: "form-select", onchange: (e) => setSort(e.target.value)}, ...[
                Object.entries(options).map(([k,v], i) => {
                    return h("option", {value:k}, v)
                })
            ])
        )
    )

}

export const HarborList = ({url, card, queryOptions, cardOptions, paginatorOptions, sortOptions}) => {

    let [data, setData] = useState(undefined);
    let [page, setPage] = useState(1);
    let [pageSize, setPageSize] = useState(10);
    let [query, setQuery] = useState("");
    let [sort, setSort] = useState("");

    let endpointUrl = new URL(url, `${window.location.protocol}//${window.location.host}`)

    endpointUrl.searchParams.set("page", page)
    endpointUrl.searchParams.set("page_size", pageSize)
    if (query) endpointUrl.searchParams.set("q", query);
    if (sort) endpointUrl.searchParams.set("sort", sort)

    useEffect(() => {let getData = async () => {
            let response = await fetch(
                endpointUrl,
                {
                    headers: {
                      'Content-Type': 'application/json'
                    },
                }
            )

            let json = await response.json()
            setData(json)
        }

        getData()

    }, [page, query, sort])

    if(data == null){
        return h("box", {className: "shine rounded project-card", style:"height:100px; width: 100%;"})
    }

    if(data.length == 0){
        return h("box", {className: "rounded project-card d-flex bg-primary", style:"height:100px; width: 100%;"}, [
            h("span", {className: "m-auto text-light"}, "No Results")
        ])
    }

    return (
        h("div", {},
            ... queryOptions || sortOptions ? [h("div", {className:"row justify-content-between mb-3"},
                ... queryOptions ? [h(QueryHandle, {className: "col-6", setQuery: setQuery})] : [],
                ... sortOptions ? [h(SortHandle, {
                    className: "col-auto",
                    options: sortOptions,
                    setSort: setSort
                })] : []
            )] : [],
            ...data.map((p) => {
                return (
                    h(card, buildOptions(cardOptions, p))
                )
            }),
            ... paginatorOptions ? [
                h(PaginateHandle, {page: page, setPage: setPage, pageSize: pageSize, url: endpointUrl, ...paginatorOptions})
            ] : []
        )
    )


}