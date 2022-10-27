import { useRef, useCallback, useEffect, useMemo, useState } from 'react';
import { useForm, Controller, useWatch } from 'react-hook-form';
import {
	Container,
	Stack,
	Typography,
	TextField,
	Switch,
	InputAdornment,
	Button,
	Paper,
	IconButton,
	CircularProgress,
	Tooltip,
	Snackbar,
	Alert,
	Box,
	Divider,
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { FileUpload } from '@mui/icons-material';
import { debounce } from 'lodash';
import {
	useLazyCreateFileJobQuery,
	useLazyCreateYoutubeJobQuery,
	useLazyArtworkQuery,
	useLazyTagsQuery,
	useLazyGroupingQuery,
} from '../../api/music';
import { isBase64, isValidImage, isValidLink, isValidYTLink, resolveAlbumFromTitle } from '../../utils/helpers';

const MusicForm = () => {
	const [openSuccess, setOpenSuccess] = useState(false);
	const [openError, setOpenError] = useState(false);
	const fileRef = useRef<HTMLInputElement>(null);

	const { reset, handleSubmit, control, trigger, setValue } = useForm<MusicFormState>({
		reValidateMode: 'onBlur',
	});
	const watchFields = useWatch({ control });

	const [createFileJob, createFileJobStatus] = useLazyCreateFileJobQuery();
	const [createYoutubeJob, createYoutubeJobStatus] = useLazyCreateYoutubeJobQuery();
	const [getArtwork, getArtworkStatus] = useLazyArtworkQuery();
	const [getTags, getTagsStatus] = useLazyTagsQuery();
	const [getGrouping, getGroupingStatus] = useLazyGroupingQuery();

	const artworkLoading = useMemo(
		() => getArtworkStatus.isLoading || getArtworkStatus.isFetching,
		[getArtworkStatus.isFetching, getArtworkStatus.isLoading]
	);

	const tagsLoading = useMemo(
		() => getTagsStatus.isLoading || getTagsStatus.isFetching,
		[getTagsStatus.isFetching, getTagsStatus.isLoading]
	);

	const jobLoading = useMemo(
		() =>
			createFileJobStatus.isLoading ||
			createFileJobStatus.isFetching ||
			createYoutubeJobStatus.isLoading ||
			createYoutubeJobStatus.isFetching,
		[
			createFileJobStatus.isFetching,
			createFileJobStatus.isLoading,
			createYoutubeJobStatus.isFetching,
			createYoutubeJobStatus.isLoading,
		]
	);

	const groupingLoading = useMemo(
		() => getGroupingStatus.isLoading || getGroupingStatus.isFetching,
		[getGroupingStatus.isFetching, getGroupingStatus.isLoading]
	);

	const onSubmit = useCallback(
		async (data: MusicFormState) => {
			if (data.fileSwitch) {
				const status = await createFileJob(data);
				if (status.isSuccess) {
					reset();
					setOpenSuccess(true);
				} else if (status.isError) {
					setOpenError(true);
				}
			} else {
				const status = await createYoutubeJob(data);
				if (status.isSuccess) {
					reset();
					setOpenSuccess(true);
				} else if (status.isError) {
					setOpenError(true);
				}
			}
		},
		[createFileJob, createYoutubeJob, reset]
	);

	const createInputLoadingAdornment = useCallback(
		(b: boolean) => <CircularProgress sx={{ display: b ? 'block' : 'none' }} size="1em" />,
		[]
	);

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const debounceResolveArtworkUrl = useCallback(
		debounce(async (artworkUrl: string) => {
			if (artworkUrl) {
				if (isBase64(artworkUrl) || isValidImage(artworkUrl)) {
					return setValue('resolvedArtworkUrl', artworkUrl);
				} else if (isValidLink(artworkUrl)) {
					const status = await getArtwork(artworkUrl);
					if (status.isSuccess) {
						const { artworkUrl } = status.data;
						return setValue('resolvedArtworkUrl', artworkUrl);
					}
				}
			}
			return setValue('resolvedArtworkUrl', '');
		}, 500),
		[]
	);

	useEffect(() => {
		debounceResolveArtworkUrl(watchFields.artworkUrl || '');
	}, [debounceResolveArtworkUrl, watchFields.artworkUrl]);

	const getFileTags = useCallback(
		async (file: File) => {
			const status = await getTags(file);
			if (status.isSuccess) {
				const { title, artist, album, grouping, artworkUrl } = status.data;
				if (title) {
					setValue('title', title);
				}
				if (artist) {
					setValue('artist', artist);
				}
				if (album) {
					setValue('album', album);
				}
				if (grouping) {
					setValue('grouping', grouping);
				}
				if (artworkUrl) {
					setValue('artworkUrl', artworkUrl);
				}
				trigger();
			}
		},
		[getTags, setValue, trigger]
	);

	useEffect(() => {
		if (watchFields.file) {
			getFileTags(watchFields.file);
		}
	}, [getFileTags, watchFields.file]);

	useEffect(() => {
		if (watchFields.title) {
			setValue('album', resolveAlbumFromTitle(watchFields.title));
		}
	}, [setValue, watchFields.title]);

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const debounceGetGrouping = useCallback(
		debounce(async (youtubeUrl: string) => {
			if (youtubeUrl) {
				if (isValidYTLink(youtubeUrl)) {
					const status = await getGrouping(youtubeUrl);
					if (status.isSuccess) {
						const { grouping } = status.data;
						setValue('grouping', grouping);
					}
				}
			}
		}, 500),
		[]
	);

	useEffect(() => {
		debounceGetGrouping(watchFields.youtubeUrl || '');
	}, [debounceGetGrouping, watchFields.youtubeUrl]);

	return useMemo(
		() => (
			<Stack direction="column" spacing={2}>
				<Snackbar
					open={openSuccess}
					onClose={() => setOpenSuccess(false)}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
				>
					<Alert severity="success">Job Started Successfully</Alert>
				</Snackbar>
				<Snackbar
					open={openError}
					onClose={() => setOpenError(false)}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
				>
					<Alert severity="error">Job Failed to Submit</Alert>
				</Snackbar>
				<Typography variant="h4">Music Downloader / Converter</Typography>
				<Divider />
				<Box>
					<Container>
						<Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={4}>
							<Stack
								direction="row"
								alignItems="center"
								spacing={{
									xs: 0,
									md: 2,
								}}
								flexWrap={{
									xs: 'wrap',
									md: 'nowrap',
								}}
							>
								<Controller
									name="youtubeUrl"
									control={control}
									defaultValue={''}
									rules={{
										required: !watchFields.fileSwitch,
										pattern: /^http(s?):\/\/(www\.)?youtube\.com\/watch\?v=.+/,
									}}
									render={({ field, fieldState }) => {
										let error = '';
										if (fieldState.error?.type === 'pattern') {
											error = 'Invalid YouTube Link';
										} else if (fieldState.error?.type === 'required') {
											error = 'Required';
										}
										return (
											<TextField
												{...field}
												error={!!error}
												helperText={error}
												label="Youtube URL"
												variant="standard"
												disabled={watchFields.fileSwitch}
												fullWidth
											/>
										);
									}}
								/>
								<Controller
									name="fileSwitch"
									control={control}
									defaultValue={false}
									render={({ field }) => <Switch {...field} checked={field.value} />}
								/>
								<Controller
									name="file"
									control={control}
									defaultValue={null}
									rules={{ required: watchFields.fileSwitch }}
									render={({ field, fieldState }) => {
										let error = '';
										if (fieldState.error?.type === 'required') {
											error = 'Required';
										}
										return (
											<TextField
												value={watchFields.file?.name || ''}
												error={!!error}
												helperText={error}
												variant="standard"
												disabled={true}
												InputProps={{
													endAdornment: (
														<InputAdornment position="end">
															<Tooltip title="Upload">
																<Box>
																	<IconButton
																		onClick={() => {
																			if (fileRef.current) {
																				const file = fileRef.current;
																				file.click();
																			}
																		}}
																		disabled={!watchFields.fileSwitch}
																	>
																		<input
																			ref={fileRef}
																			onChange={(e) => {
																				const files = e.target.files;
																				if (files) {
																					const file = files[0];
																					setValue('file', file);
																					trigger();
																				}
																			}}
																			onBlur={field.onBlur}
																			hidden
																			type="file"
																			accept="audio/*"
																		/>
																		<FileUpload />
																	</IconButton>
																</Box>
															</Tooltip>
														</InputAdornment>
													),
												}}
												fullWidth
											/>
										);
									}}
								/>
							</Stack>
							<Stack
								direction="row"
								alignItems="center"
								spacing={{
									xs: 0,
									md: 2,
								}}
								flexWrap={{
									xs: 'wrap',
									md: 'nowrap',
								}}
							>
								<Paper variant="outlined">
									<img
										alt="blank"
										width="100%"
										src={
											watchFields.resolvedArtworkUrl ||
											'https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg'
										}
									/>
								</Paper>
								<Stack
									spacing={2}
									direction="column"
									width={{
										xs: '100%',
										md: '50%',
									}}
								>
									<Controller
										name="artworkUrl"
										control={control}
										defaultValue={''}
										render={({ field, fieldState }) => (
											<TextField
												{...field}
												error={!!fieldState.error}
												helperText={fieldState.error?.message}
												label="Artwork URL"
												variant="standard"
												fullWidth
												disabled={tagsLoading}
											/>
										)}
									/>
									<Controller
										name="resolvedArtworkUrl"
										control={control}
										defaultValue={''}
										render={({ field }) => (
											<TextField
												{...field}
												label="Resolved Artwork URL"
												variant="standard"
												fullWidth
												disabled
												InputProps={{
													endAdornment: createInputLoadingAdornment(artworkLoading || tagsLoading),
												}}
											/>
										)}
									/>
									<Button onClick={() => setValue('artworkUrl', '')}>Clear</Button>
								</Stack>
							</Stack>
							<Stack
								direction="row"
								justifyContent="space-around"
								spacing={{
									xs: 0,
									md: 2,
								}}
								flexWrap={{
									xs: 'wrap',
									md: 'nowrap',
								}}
							>
								<Controller
									name="title"
									control={control}
									defaultValue={''}
									rules={{ required: true }}
									render={({ field, fieldState }) => {
										let error = '';
										if (fieldState.error?.type === 'required') {
											error = 'Required';
										}
										return (
											<TextField
												{...field}
												error={!!error}
												helperText={error}
												label="Title"
												variant="standard"
												fullWidth
												disabled={tagsLoading}
												InputProps={{
													endAdornment: createInputLoadingAdornment(tagsLoading),
												}}
											/>
										);
									}}
								/>
								<Controller
									name="artist"
									control={control}
									defaultValue={''}
									rules={{ required: true }}
									render={({ field, fieldState }) => {
										let error = '';
										if (fieldState.error?.type === 'required') {
											error = 'Required';
										}
										return (
											<TextField
												{...field}
												error={!!error}
												helperText={error}
												label="Artist"
												variant="standard"
												fullWidth
												disabled={tagsLoading}
												InputProps={{
													endAdornment: createInputLoadingAdornment(tagsLoading),
												}}
											/>
										);
									}}
								/>
								<Controller
									name="album"
									control={control}
									defaultValue={''}
									rules={{ required: true }}
									render={({ field, fieldState }) => {
										let error = '';
										if (fieldState.error?.type === 'required') {
											error = 'Required';
										}
										return (
											<TextField
												{...field}
												error={!!error}
												helperText={error}
												label="Album"
												variant="standard"
												fullWidth
												disabled={tagsLoading}
												InputProps={{
													endAdornment: createInputLoadingAdornment(tagsLoading),
												}}
											/>
										);
									}}
								/>
								<Controller
									name="grouping"
									control={control}
									defaultValue={''}
									render={({ field }) => (
										<TextField
											{...field}
											label="Grouping"
											variant="standard"
											fullWidth
											disabled={tagsLoading || groupingLoading}
											InputProps={{
												endAdornment: createInputLoadingAdornment(tagsLoading || groupingLoading),
											}}
										/>
									)}
								/>
							</Stack>
							<Stack
								direction="row"
								justifyContent="center"
								spacing={2}
								flexWrap={{
									xs: 'wrap',
									md: 'nowrap',
								}}
							>
								<LoadingButton
									disabled={artworkLoading || tagsLoading || groupingLoading}
									loading={jobLoading}
									variant="contained"
									type="submit"
								>
									Download / Convert
								</LoadingButton>
								<Button variant="contained" onClick={() => reset()}>
									Reset
								</Button>
							</Stack>
						</Stack>
					</Container>
				</Box>
			</Stack>
		),
		[
			openSuccess,
			openError,
			handleSubmit,
			onSubmit,
			control,
			watchFields.fileSwitch,
			watchFields.resolvedArtworkUrl,
			watchFields.file?.name,
			artworkLoading,
			tagsLoading,
			groupingLoading,
			jobLoading,
			setValue,
			trigger,
			createInputLoadingAdornment,
			reset,
		]
	);
};

export default MusicForm;
