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

export const ProjectCard = ({
    name,
    href,
    repo_count,
    update_time,
    chart_count,
    creation_time,
    ...props
}) => {
    let localeUpdateTime = new Date(Date.parse(update_time)).toLocaleString("en-US")
    let localeCreationTime = new Date(Date.parse(creation_time)).toLocaleString("en-US")

    return (
        h("a", {href: href, className:"text-decoration-none"},
            h(
                ImageCard,
                {src: "/static/images/icons/building.svg", alt: "Building Graphic", className: "project-card mb-1 mb-sm-2 p-3 rounded bg-light"},
                h("div", {className: "description"}, ...[
                    h("div", {className: "row gx-2"}, ...[
                        h("h4", {className: "col-12 col-md-auto fw-bold mb-1"}, name),
                        ... repo_count ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/Repo_Icon.svg",
                            alt: "Repository Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Repositories: ${repo_count}`,
                            text: `${repo_count} Repositories`
                        })] : [],
                        ... chart_count ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/map-fill.svg",
                            alt: "Map Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Charts: ${chart_count}`,
                            text: `${chart_count} Charts`
                        })] : [],
                    ]),
                    h("div", {className: "row gx-2"}, ...[
                        h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/clock-history.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            text: `Updated ${localeUpdateTime}`
                        }),
                        h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/clock.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            text: `Created ${localeCreationTime}`
                        }),
                    ])
                ])
            )
        )
    )
}

export const RepositoryCard = ({
    name,
    project_id,
    pull_count,
    artifact_count,
    update_time,
    chart_count,
    creation_time,
    ...props
}) => {
    let localeUpdateTime = new Date(Date.parse(update_time)).toLocaleString("en-US")
    let localeCreationTime = new Date(Date.parse(creation_time)).toLocaleString("en-US")

    let [project, repository] = name.split("/")

    return (
        h("a", {href: `https://hub.opensciencegrid.org/harbor/projects/${project_id}/repositories/${repository}`, className:"text-decoration-none"},
            h(
                ImageCard,
                {src: "/static/images/icons/Repo_Icon.svg", alt: "Building Graphic", className: "project-card  mb-1 mb-sm-2 p-3 rounded bg-light"},
                h("div", {className: "description"}, ...[
                    h("div", {className: "row gx-2"}, ...[
                        h("h4", {className: "col-12 col-md-auto fw-bold mb-1"}, repository),
                        ... pull_count ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/download.svg",
                            alt: "Repository Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Pull Count: ${pull_count.toLocaleString()}`,
                            text: `${pull_count.toLocaleString()} Pulls`
                        })] : [],
                        ... artifact_count ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/artifact-registry.svg",
                            alt: "Repository Artifact Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Artifact Count: ${artifact_count.toLocaleString()}`,
                            text: `${artifact_count.toLocaleString()} Artifacts`
                        })] : [],
                    ]),
                    h("div", {className: "row gx-2"}, ...[
                        h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/clock-history.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            text: `Updated ${localeUpdateTime}`
                        }),
                        h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/clock.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            text: `Created ${localeCreationTime}`
                        }),
                    ])
                ])
            )
        )
    )
}