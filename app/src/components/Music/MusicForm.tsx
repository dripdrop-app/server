import { useRef, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
	Container,
	Stack,
	Box,
	Typography,
	TextField,
	Switch,
	InputAdornment,
	Button,
	Paper,
	IconButton,
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { FileUpload } from '@mui/icons-material';
import { useLazyCreateFileJobQuery, useLazyCreateYoutubeJobQuery } from '../../api/music';

const MusicForm = () => {
	const fileRef = useRef<HTMLInputElement>(null);

	const { reset, handleSubmit, control, watch, trigger, setValue } = useForm<MusicFormState>({
		reValidateMode: 'onBlur',
	});

	const [createFileJob, createFileJobStatus] = useLazyCreateFileJobQuery();
	const [createYoutubeJob, createYoutubeJobStatus] = useLazyCreateYoutubeJobQuery();

	const onSubmit = useCallback(
		(data: MusicFormState) => {
			if (data.fileSwitch) {
				createFileJob(data).then((status) => {
					if (status.isSuccess) {
						reset();
					}
				});
			} else {
				createYoutubeJob(data).then((status) => {
					if (status.isSuccess) {
						reset();
					}
				});
			}
		},
		[createFileJob, createYoutubeJob, reset]
	);

	return (
		<Container sx={{ paddingY: 2 }}>
			<Box>
				<Typography variant="h4">Music Downloader / Converter</Typography>
				<Stack component="form" onSubmit={handleSubmit(onSubmit)} paddingY={4} paddingX={2} spacing={4}>
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
							rules={{ required: !watch('fileSwitch') }}
							render={({ field, fieldState }) => (
								<TextField
									{...field}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									label="Youtube URL"
									variant="standard"
									disabled={watch('fileSwitch')}
									fullWidth
								/>
							)}
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
							rules={{ required: watch('fileSwitch') }}
							render={({ field, fieldState }) => (
								<TextField
									value={watch('file')?.name || ''}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									variant="standard"
									disabled={true}
									InputProps={{
										endAdornment: (
											<InputAdornment position="end">
												<IconButton
													onClick={() => {
														if (fileRef.current) {
															const file = fileRef.current;
															file.click();
														}
													}}
													disabled={!watch('fileSwitch')}
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
											</InputAdornment>
										),
									}}
									fullWidth
								/>
							)}
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
								src="https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg"
							/>
						</Paper>
						<Stack
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
									/>
								)}
							/>
							<TextField label="Resolved Artwork URL" variant="standard" fullWidth disabled />
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
							render={({ field, fieldState }) => (
								<TextField
									{...field}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									label="Title"
									variant="standard"
									fullWidth
								/>
							)}
						/>
						<Controller
							name="artist"
							control={control}
							defaultValue={''}
							rules={{ required: true }}
							render={({ field, fieldState }) => (
								<TextField
									{...field}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									label="Artist"
									variant="standard"
									fullWidth
								/>
							)}
						/>
						<Controller
							name="album"
							control={control}
							defaultValue={''}
							rules={{ required: true }}
							render={({ field, fieldState }) => (
								<TextField
									{...field}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									label="Album"
									variant="standard"
									fullWidth
								/>
							)}
						/>
						<Controller
							name="grouping"
							control={control}
							defaultValue={''}
							render={({ field, fieldState }) => (
								<TextField
									{...field}
									error={!!fieldState.error}
									helperText={fieldState.error?.message}
									label="Grouping"
									variant="standard"
									fullWidth
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
							loading={
								createFileJobStatus.isLoading ||
								createFileJobStatus.isFetching ||
								createYoutubeJobStatus.isLoading ||
								createYoutubeJobStatus.isFetching
							}
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
			</Box>
		</Container>
	);
};

export default MusicForm;
