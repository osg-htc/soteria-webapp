import { h, Component, render } from 'https://cdn.skypack.dev/preact@10.4.7';
import { useEffect, useState, useRef, useMemo } from 'https://cdn.skypack.dev/preact@10.4.7/hooks'



export const ImageTextRow = ({src, alt, tag, text, imgStyle, ...props}) => {

    return (
        h("div", {...props, className: `image-text-row ${props.className}`}, ...[
            h("img", {src: src, alt: alt}),
            h(tag ? tag : "span", {}, text)
        ])
    )
}

export const ImageCard = ({
    src,
    alt,
    children,
    ...props
}) => {
    return (
        h("div", {...props},
            h("div", {className: "row image-card"},
                h(
                    "div",
                    {
                        className: "col-auto d-none d-sm-flex",
                    },
                    h(
                        "img",
                        {
                            src: src,
                            alt: alt,
                        }
                    )
                ),
                h(
                    "div",
                    {
                        className: "col-10",
                    },
                    children
                ),
            )
        )
    )
}