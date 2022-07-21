args = commandArgs(trailingOnly=TRUE)
library(NASAaccess)
library(remotes)
library(emayili)
a <- strsplit(args[2],",")

start_d <- strsplit(args[7],",")
end_d <- strsplit(args[8],",")
nexgdpp <- strsplit(args[9],",")
nextgdppcmip <- strsplit(args[10],",")

b <- a[[1]]
ca <- ""


tryCatch(
    expr = {
		for(x in a[[1]]){
			print(x)
			ca <- x
			
			if(x == "GLDASpolyCentroid"){
				GLDASpolyCentroid(
					Dir =paste(args[6],"/GLDASpolyCentroid/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][1],
					end = end_d[[1]][1]
					)

			}
			if(x == "GPM_NRT"){
				GPM_NRT(
					Dir =paste(args[6],"/GPM_NRT/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][2],
					end = end_d[[1]][2]
					)
			}
			if(x == "GPMswat"){
				GPMswat(
					Dir =paste(args[6],"/GPMswat/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][3],
					end = end_d[[1]][3]
					)
			}
			if(x == "GPMpolyCentroid"){
				GPMpolyCentroid(
					Dir =paste(args[6],"/GPMpolyCentroid/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][4],
					end = end_d[[1]][4]
					)
			}
			if(x == "GLDASwat"){
				GLDASwat(
					Dir =paste(args[6],"/GLDASwat/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][5],
					end = end_d[[1]][5]
					)
			}
			if(x == "NEX_GDDP_CMIP5"){
				NEX_GDDP_CMIP5(
					Dir =paste(args[6],"/NEXGDPP/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][6],
					end = end_d[[1]][6],
					model = nexgdpp[[1]][1],
					type = nexgdpp[[1]][2],
					slice = nexgdpp[[1]][3]
					)
			}
			if(x == "NEX_GDDP_CMIP6"){
				NEX_GDDP_CMIP6(
					Dir =paste(args[6],"/NEX_GDPP_CMIP6/",sep=""),
					watershed = args[4],
					DEM = args[5],
					start = start_d[[1]][7],
					end = end_d[[1]][7],
					model = nextgdppcmip[[1]][1],
					type = nextgdppcmip[[1]][2],
					slice = nextgdppcmip[[1]][3]
					)
			}

		}
    },
    error = function(e){ 
        # (Optional)
        # Do t"his if an error is caught.
		print("we have an error")
		nb <- get("b", env=globalenv())
		nb <- nb[! nb %in% c(ca)]
		assign("b", nb, env=globalenv())
		print(e)
    },
    warning = function(w){
        # (Optional)
        # Do this if an warning is caught...
    },
    finally = {
		print("printing b")
		print(get("b", env=globalenv()))
		zero_check <- paste("<html><head></head><body><p>Hello,<br>Your nasaaccess data is ready for download for the following functions" , toString(get("b", env=globalenv())), " <br>Please use the unique access code: <strong>", args[3], "</strong><br></p></body><html>")

		if (identical(get("b", env=globalenv()), character(0)) ) {
			zero_check <- paste("<html><head></head><body><p>None of the selected functions were able to provide data.</p></body><html>")
		}
		email <- envelope(
		to = args[1],
		from = "nasaaccess.2022@gmail.com",
		subject = 'Your nasaaccess data is ready',
		#   html =paste("<html><head></head><body><p>Hello,<br>Your nasaaccess data is ready for download at <a href='http://127.0.0.1:8000/apps/nasaaccess'>http://localhost:8080/apps/nasaaccess</a><br>Your unique access code is: <strong>", args[3], "</strong><br></p></body><html>")
		# html =paste("<html><head></head><body><p>Hello,<br>Your nasaaccess data is ready for download for the following functions" , toString(get("b", env=globalenv())), " <br>Please use the unique access code: <strong>", args[3], "</strong><br></p></body><html>")
		html = zero_check
		)

		smtp <- server(host = "smtp.gmail.com",
					port = 587,
					username = 'nasaaccess.2022@gmail.com',
					password = 'zdfsfvmtpbowdmgi')
		smtp(email, verbose = TRUE)
    }
)



#zdfsfvmtpbowdmgi
# nasaaccess123&