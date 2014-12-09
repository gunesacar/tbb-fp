library(RColorBrewer)
rf <- colorRampPalette(rev(brewer.pal(11,'Spectral')))
r <- rf(32)
read.csv("/home/gunes/dev/tor/tbb-fp/scr.txt.csv", header = TRUE) -> res
wrep= as.vector(rep(res$w, res$freq))
hrep= as.vector(rep(res$h, res$freq))
crep= as.vector(rep(res$c, res$freq))

df = data.frame(wrep, hrep)
library(ggplot2)

# Default call (as object)
p <- ggplot(df, aes(wrep, hrep))
h3 <- p + stat_bin2d()
h3
p + stat_bin2d(bins=100) + scale_fill_gradientn(colours=r, trans="log")
# qplot(wrep, hrep, data = df, geom="bin2d", xlim = c(0, 2000), ylim = c(0, 2000))
# binwidth = c(0.1, 0.1),

require("hexbin")
hbin <- hexbin(wrep, hrep, xbins = 40)
#plot(hbin)
plot(hbin, colramp=rf)

require(KernSmooth)
z <- bkde2D(df, .5)
persp(z$fhat)