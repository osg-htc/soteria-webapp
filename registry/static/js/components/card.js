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
    quota,
    ...props
}) => {
    let localeUpdateTime = new Date(Date.parse(update_time)).toLocaleString("en-US")
    let localeCreationTime = new Date(Date.parse(creation_time)).toLocaleString("en-US")

    let quotaDetails = null
    let usedGiB = -1
    let limitGiB = -1

    if (quota && "used" in quota && "storage" in quota.used) {
      let usedBytes = quota.used.storage
      usedGiB = Math.round(usedBytes / 1024 / 1024 / 1024 * 100) / 100
    }
    if (quota && "hard" in quota && "storage" in quota.hard) {
      let limitBytes = quota.hard.storage
      limitGiB = Math.round(limitBytes / 1024 / 1024 / 1024 * 100) / 100
    }

    if (usedGiB > 0 && limitGiB > 0) {
      quotaDetails = `Used ${usedGiB} GiB out of ${limitGiB} GiB`
    }
    else if (usedGiB > 0) {
      quotaDetails = `Used ${usedGiB} GiB`
    }

    if (quotaDetails) {
      quotaDetails = h("div", {className: "row gx-2"}, ...[
                        h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/database-fill.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            text: quotaDetails,
                        })
                    ])
    }

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
                    ]),
                    quotaDetails
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
        h("a", {href: `/public/projects/${project}/repositories/${repository}/tags`, className:"text-decoration-none"},
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

export const TagCard = ({
  project,
  repository,
  digest,
  pull_time,
  push_time,
  tags
}) => {
    let localePushTime = new Date(Date.parse(push_time)).toLocaleString("en-US")
    let localePullTime = new Date(Date.parse(pull_time)).toLocaleString("en-US")

    if(tags === null) {
        return null
    }

    return (
        h("a", {href: `/public/projects/${project}/repositories/${repository}/tags/${tags?.[0].name}`, className:"text-decoration-none"},
            h(
                ImageCard,
                {src: "/static/images/icons/tags-white.svg", alt: "Tag Graphic", className: "project-card  mb-1 mb-sm-2 p-3 rounded bg-light"},
                h("div", {className: "description"}, ...[
                    h("div", {className: "row gx-2"}, ...[
                        h("h4", {className: "col-12 col-md-auto fw-bold mb-1"}, digest.substring(0, 10)),
                    ]),
                    h("div", {className: "row gx-2"}, ...[
                        ... push_time ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/upload.svg",
                            alt: "Repository Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Push Time: ${localePushTime}`,
                            text: `Push Time: ${localePushTime}`
                        })] : [],
                    ]),
                    h("div", {className: "row gx-2  text-truncate"}, ...[
                        ... push_time ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/download.svg",
                            alt: "Repository Graphic",
                            tag: "h6",
                            "data-bs-toggle": "tooltip",
                            "data-bs-placement": "top",
                            title: `Pull Time: ${localePullTime}`,
                            text: `Pull Time: ${localePullTime}`
                        })] : [],
                    ]),
                    h("div", {className: "row gx-2  text-truncate"}, ...[
                        ... tags ? [h(ImageTextRow, {
                            className: "col-auto",
                            src: "/static/images/icons/tags.svg",
                            alt: "Download Graphic",
                            tag: "h6",
                            title: `${tags.length} Tags`,
                            text: `${tags.length} Tags: ${tags.reverse().map(x => x.name).join(", ")}`
                        })] : [],
                    ])
                ])
            )
        )
    )
}
