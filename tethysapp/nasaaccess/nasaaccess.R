args = commandArgs(trailingOnly=TRUE)
library(NASAaccess)
library(remotes)
library(emayili)
a <- strsplit(args[2],",")

start_d <- strsplit(args[7],",")
end_d <- strsplit(args[8],",")
nexgdpp <- strsplit(args[9],",")
nextgdppcmip <- strsplit(args[10],",")




for(x in a[[1]]){


if(x == "GLDASpolyCentroid"){

	GLDASpolyCentroid(
		  Dir =paste(args[6],"/GLDASpolyCentroid/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9]
		  start = start_d[[1]][1],
		  end = end_d[[1]][1]
		)
}
if(x == "GPMswat"){

	GPMswat(
		  Dir =paste(args[6],"/GPMswat/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9]
		  start = start_d[[1]][2],
		  end = end_d[[1]][2]
		)
}
if(x == "GPMpolyCentroid"){

	GPMpolyCentroid(
		  Dir =paste(args[6],"/GPMpolyCentroid/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9]
		  start = start_d[[1]][3],
		  end = end_d[[1]][3]
		)
}
if(x == "GLDASwat"){

	GLDASwat(
		  Dir =paste(args[6],"/GLDASwat/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9]
		  start = start_d[[1]][4],
		  end = end_d[[1]][4]
		)
}
if(x == "NEXT_GDPPswat"){

	NEX_GDPPswat(
		  Dir =paste(args[6],"/NEXGDPP/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9],
		  start = start_d[[1]][5],
		  end = end_d[[1]][5],
		  model = nexgdpp[[1]][1],
		  type = nexgdpp[[1]][2],
          slice = nexgdpp[[1]][3]
		)
}
if(x == "NEX_GDPP_CMIP6"){

	NEX_GDPP_CMIP6(
		  Dir =paste(args[6],"/NEX_GDPP_CMIP6/",sep=""),
		  watershed = args[4],
		  DEM = args[5],
		#   start = args[8],
		#   end = args[9],
		  start = start_d[[1]][6],
		  end = end_d[[1]][6],
		  model = nextgdppcmip[[1]][1],
		  type = nextgdppcmip[[1]][2],
          slice = nextgdppcmip[[1]][3]
		)
}
}


email <- envelope(
  to = args[1],
  from = "nasaaccess.2022@gmail.com",
  subject = 'Your nasaaccess data is ready',
  html =paste("<html><head></head><body><p>Hello,<br>Your nasaaccess data is ready for download at <a href='http://127.0.0.1:8000/apps/nasaaccess'>http://localhost:8080/apps/nasaaccess</a><br>Your unique access code is: <strong>", args[3], "</strong><br></p></body><html>")
)

smtp <- server(host = "smtp.gmail.com",
               port = 587,
               username = 'nasaaccess.2022@gmail.com',
               password = 'nasaaccess123&')
smtp(email, verbose = TRUE)