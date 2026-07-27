HW2
================
Kai Barclay
2026-07-27

# Homework 2

Let’s get our libraries set up first.

`{r} library(igraph) library(ggplot2) library(ggraph) set.seed(42)`

Next, let’s get our data.

`{r} dataGitLink='https://github.com/KaiFish/DACSS-690C-Homework/raw/main/hollywood.graphml' actors=read_graph(dataGitLink,format='graphml') summary(actors)`

## Central Measures and Hubs

We are going to calculate our nodes’ central measures…

\`\`\`{r} eigen=eigen_centrality (actors)\$vector

close=closeness(actors,normalized=T)

betw=betweenness(actors,normalized=T)

DFCentrality=as.data.frame(cbind(eigen,close,betw),stringsAsFactors = F)
names(DFCentrality)=c(‘Eigenvector’,‘Closeness’,‘Betweenness’)

DFCentrality\$person=row.names(DFCentrality)
row.names(DFCentrality)=NULL


    ... and make a correlation plot of our results.

    ```{r}
    ggplot(DFCentrality, aes(x=Betweenness, y=Closeness)) + 
        theme_classic() +
        geom_text(aes(label=person,size=Eigenvector),show.legend = T,alpha=0.5) 

We can see Robin Williams clearly, but their are two names that are
overlapping and hard to read. To see those:

`{r} HubNodes=dplyr::slice_max(DFCentrality, order_by = Eigenvector, n = 2)$person HubNodes`

Al Pacino and Robert De Niro have been in multiple films together,
unlike the other actors in this graph.

Let’s see our plot with our hub nodes highlighted:

\`\`\`{r} NodeCount=length(V(actors))

V(actors)\$label=’’

for (index in seq(1:NodeCount)){ currentName=V(actors)$name[index]
    if (currentName%in%HubNodes){
            V(actors)$label\[index\]=currentName } }

base=ggraph(graph = actors) base + geom_node_label(aes(label = label),
repel = TRUE, show.legend = F, color=‘red’) + geom_edge_link(alpha=0.1,
aes(label=weight, edge_width=weight))


    (De Niro and Pacino have now been in 4 films together, the most recent being *The Irishman* in 2019)

    ## Evaluate Possible Communities

    Let's calculate the possibility of community emergence. First, we need a distribution of a random network to calculate the mean random transitivity.

    ```{r}
    setseed(53)
    # Generate an ensemble of 1000 rewired random networks 
    replicates <- 1000  
    random_transitivities <- replicate(replicates, {
      RandomNet <- rewire(actors, 
                          keeping_degseq(niter = gsize(actors) * 10))
      transitivity(RandomNet, type = "global")
    })
    mean_random_transitivities=mean(random_transitivities)

Next, we will calculate the empirical transitivity we observe in our
graph.

`{r} # Calculate your empirical transitivity empirical_transitivity <- transitivity(actors, type = "global")`

Finally, we will calculate the ratio between our observed and random
transitivities.

`{r} report_table <- data.frame(   Metric = c("Actors transitivity", "Random-network mean", "Ratio"),   Value  = round(c(empirical_transitivity,                     mean_random_transitivities,                     empirical_transitivity / mean_random_transitivities), 4) ) knitr::kable(report_table)`

With a ratio greater than one, we may assess using our
community-detection algorithms. We will use all five for comparison’s
sake.

\`\`\`{r} \# Run all five community-detection algorithms algos \<- list(
louvain = { set.seed(123); cluster_louvain(actors) }, walktrap =
cluster_walktrap(actors), fast_greedy = cluster_fast_greedy(actors),
infomap = cluster_infomap(actors), edge_betweenness =
cluster_edge_betweenness(actors) )

# Build a summary table: number of clusters, modularity (Q), and cluster sizes

summary_table \<- data.frame( algorithm = names(algos), n_clusters =
sapply(algos, length), modularity_Q = sapply(algos, modularity),
cluster_sizes = sapply(algos, function(cl) { paste(sort(sizes(cl),
decreasing = TRUE), collapse = “,”) }) )

# Sort by modularity, descending, so the “best” partition (by this metric) is on top

summary_table \<- summary_table\[order(-summary_table\$modularity_Q), \]
rownames(summary_table) \<- NULL

print(summary_table)


    All of the algorithms have a modularity above 0.4, indicating strong communities. Though all of the results were very close, we will use walktrap in the next section as it listed as our top result.

    First, we will add our community ids as attributes for ease of use later.

    ```{r}
    for (name in names(algos)) {
      memb <- membership(algos[[name]])
      attr_name <- name
      actors <- set_vertex_attr(actors, attr_name,
                                   index = names(memb),
                                  # this is important for exporting
                                   value = as.vector(memb))
    }
    # verify new attributes
    vertex_attr_names(actors)

With that done, we can then use walktrap to graph our best result.

\`\`\`{r} base=ggraph(graph =actors) + geom_edge_link(alpha=0.2)

base + geom_node_point(aes(color=as.factor(walktrap)), show.legend = T,
size=4) \`\`\`
