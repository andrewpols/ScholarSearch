updateSearchHistory(searchHistory);

const width = window.screen.width, height = window.screen.height;
const color = d3.scaleOrdinal(d3.schemeCategory10);
const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .attr("style", "max-width: 100%; height: auto; ");

// Create simulation
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(d => -d.weight * 23))
    .force("x", d3.forceX())
    .force("y", d3.forceY())

// Draw links
const link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("class", "link");

let lastNodeHovered;
let lastNodeGroup;
let lastPaper;

// Draw nodes
const node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("class", "node")
    .attr("r", d => d.weight * 3)
    .attr("fill", d => color(d.group))
    .call(d3.drag()
        .on("start", dragStarted)
        .on("drag", dragged)
        .on("end", dragEnded)
    ).on("mouseenter", (event, d) => {
        if (!isDragging) {
            if (event.currentTarget !== lastNodeHovered) {
                d3.select(lastNodeHovered).style("fill", color(lastNodeGroup))
            }

            label.filter(l => l.id === d.id).style("display", "block");
            document.getElementById("paper-title").innerText = d.title;
            document.getElementById("paper-author").innerText = d.authors[0];
            d3.select(event.currentTarget).style("fill", "rgb(98, 255, 0)");

            document.getElementById("abstract-toggle").style.visibility = "visible";

            if (document.getElementById("abstract-toggle").innerText === "Hide Abstract") {
                document.getElementById("paper-abstract").innerText = truncateString(d.abstract);
            }

            lastNodeHovered = event.currentTarget;
            lastNodeGroup = d.group;
            lastPaper = d;

        }
    })
    .on("mouseleave", (event, d) => {
        if (!isDragging) {
            label.filter(l => l.id === d.id).style("display", "none");
        }
    })
    .on('click', (event, d) => {
        const title = encodeURIComponent(d.title);
        const author = encodeURIComponent(d.authors[0]);
        window.open(`/loading?title=${title}&author=${author}`, '_blank');
    });

// Add labels
const label = svg.append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(nodes)
    .enter().append("text")
    .attr("class", "label")
    .text(d => d.title).style("display", "none");

// Update positions on every tick
simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    label
        .attr("x", d => d.x + d.weight * 3.2)
        .attr("y", d => d.y);
});

// Dragging behavior
function dragStarted(event, d) {
    isDragging = true;
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    isDragging = false;
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function updateSearchHistory(searchHistory) {
    i = searchHistory.length - 1

    console.log(i);
    console.log('here');

    while (i >= 0 && i < searchHistory.length && i > searchHistory.length - 4) {
        const historyBar = document.getElementById(`hist${searchHistory.length - i}`);
        const queryInfo = document.getElementById(`query${searchHistory.length - i}`);
        historyBar.innerText = searchHistory[i];
        queryInfo.value = searchHistory[i];
        i--;
    }

}

function truncateString(s) {
    const maxLength = 200;

    return s.slice(0, maxLength) + "...";
}

document.querySelectorAll('.submit-btn')
    .forEach(function (button) {
        button.addEventListener("click", function (event) {
            const buttonText = button.innerText;
            const form = event.target.closest("form");

            if (buttonText) {
                form.submit()
            } else {
                event.preventDefault();
            }
        })
    })

const abstractBtn = document.getElementById("abstract-toggle");
abstractBtn.addEventListener("click", function (event) {
    const toggleOnText = "View Abstract";
    const toggleOffText = "Hide Abstract";
    const abstractText = document.getElementById("paper-abstract");

    if (abstractBtn.innerText === toggleOnText) {
        abstractBtn.innerText = toggleOffText;

        abstractText.innerText = truncateString(lastPaper.abstract);

    } else {
        abstractBtn.innerText = toggleOnText;
        abstractText.innerText = "";
    }
});

// Append SVG to the body (or another container)
document.getElementById("graph").appendChild(svg.node());
