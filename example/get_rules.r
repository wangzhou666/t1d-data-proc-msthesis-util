setwd("/Users/zhouwang/Desktop/thesis-code")

features <- read.csv("example/output/example-features.csv")
labels <- read.csv("example/output/example-labels.csv")

y <- labels["T1D"]
y[y==0] <- -1

X <- features

library(inTrees)
library(randomForest); library(RRF); library(gbm);

imputedX <- rfImpute(X, as.factor(y[,c('T1D')]), ntree=5, iter=5)
imputedX <- subset(imputedX, select=-c(as.factor(y[, c("T1D")])))

rf <- randomForest(imputedX, as.factor(y[,c('T1D')]), ntree=500, maxnodes=4)
treeList <- RF2List(rf)
rules <- extractRules(treeList, imputedX, ntree=500)
rules <- unique(rules)

outfile <- file("example/output/example-rules.txt")
writeLines(rules, outfile)
close(outfile)

sink("example/output/example-feature-list.txt")
colX <- colnames(X)
for (i in 1 : length(colX)) {
    cat(i-1)
    cat(',')
    cat(colX[i])
    cat('\n')
}
sink()