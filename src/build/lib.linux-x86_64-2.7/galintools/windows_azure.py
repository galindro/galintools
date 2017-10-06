#!/usr/bin/python
from galintools import infra_common
from azure.storage import BlobService
from datetime import datetime
import os, syslog, progressbar

class AzureBlobService():
	
	def __init__(self, logger, account_name, account_key):
		self.logger = logger
		self.blob_service = BlobService(account_name=account_name, account_key=account_key)
		self.pbar = None

	def azure_sync(self, root_path, container, check=False):
		return_code = 0

		if not os.path.exists(root_path):
			self.logger.error("Error in sync file %s to azure. Details: No such file or directory" % (root_path))
			return_code = 1
		else:
			dt_start = datetime.now()
			self.logger.info("Syncing files from %s to azure container %s" % (root_path, container))
			for root, dirs, files in os.walk(root_path, topdown=False):
				for name in files:
					blob_metadata = {}
					path = os.path.join(root, name)

					mtime = str(os.path.getmtime(path))

					try:
						self.logger.debug("file: %s - Checking file modification time with azure API" % (path))
						blob_metadata = self.blob_service.get_blob_metadata(container, path)
					except Exception, e:
						if type(e).__name__ != 'WindowsAzureMissingResourceError':
							self.logger.error("file: %s - Can't check file modification time with azure API. Details: %s - %s" % (path, type(e).__name__, str(e)))
							return_code = return_code + 1
							continue
						else:
							pass

				if ('x-ms-meta-mtime' not in blob_metadata) or (blob_metadata['x-ms-meta-mtime'] != mtime):
						return_code = return_code + self.azure_send(container, path, mtime)

		dt_finish = datetime.now()
		dt_elapsed = dt_finish - dt_start

		if return_code == 0:
			self.logger.info("Sync files from %s to azure finished successfully. Time to sync: %s" % (root_path, dt_elapsed))
		else:
			self.logger.error("Sync files from %s to azure finished with %i errors. Time to sync: %s" % (root_path, return_code, dt_elapsed))

		return return_code


	def upload_progress(self, current, total):
		self.pbar.update(current)

	def azure_send(self, container, path, mtime):
		return_code = 0

		if not os.path.exists(path):
			self.logger.error("%s - Error sync file to azure. Details: No such file or directory" % (path))
			return_code = 1
		else:
			try:
				file_size = os.path.getsize(path)

				if file_size == 0:
					file_size = 1

				self.pbar = progressbar.ProgressBar(widgets=["Sending data to Azure", 
															 progressbar.Percentage(), 
															 ' ', 
															 progressbar.Bar(marker=progressbar.RotatingMarker()), 
															 ' ', 
															 progressbar.ETA(), 
															 ' ', 
															 progressbar.FileTransferSpeed()], 
															 maxval=file_size).start()
				self.blob_service.put_block_blob_from_path(container, path, path, progress_callback=self.upload_progress)
				self.pbar.finish()
				self.blob_service.set_blob_metadata(container, path, x_ms_meta_name_values={"mtime":str(mtime)})

			except (ValueError, ZeroDivisionError):
				pass
			except Exception, e:
				self.logger.error("%s - Error sync file to azure. Details: %s" % (path, str(e)))
				return_code = 1
				pass

		return return_code

