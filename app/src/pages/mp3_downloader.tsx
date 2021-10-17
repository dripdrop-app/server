import React, { useState, useRef } from 'react';
import {
	Box,
	Container,
	Divider,
	Typography,
	TextField,
	Switch,
	Button,
	ContainerProps,
	TextFieldProps,
} from '@mui/material';
import { YouTube } from '@mui/icons-material';
import Image from '../images/blank_image.jpeg';
import { FILE_TYPE } from '../utils/enums';

const MP3Downloader = () => {
	const [validForm, setValidForm] = useState(false);

	const [fileType, setFileType] = useState(FILE_TYPE.YOUTUBE);

	const [youTubeURL, setYouTubeURL] = useState('');
	const [fileName, setFileName] = useState('');
	const [validYouTubeURL, setValidYouTubeURL] = useState(true);

	const [artworkURL, setArtworkURL] = useState('');
	const [validArtworkURL, setValidArtworkURL] = useState(true);

	const [title, setTitle] = useState('');
	const [artist, setArtist] = useState('');
	const [album, setAlbum] = useState('');
	const [grouping, setGrouping] = useState('');

	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	const validateForm = () => {
		let valid = true;
		if (fileType === FILE_TYPE.YOUTUBE) {
			valid = validYouTubeURL && valid;
		} else if (fileType === FILE_TYPE.MP3_UPLOAD || fileType === FILE_TYPE.WAV_UPLOAD) {
			valid = fileName !== '' && valid;
		}
		setValidForm(valid);
	};

	const reset = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
		setValidForm(false);
		setFileType(FILE_TYPE.YOUTUBE);
		setYouTubeURL('');
		setFileName('');
		setValidYouTubeURL(true);
		setArtworkURL('');
		setValidArtworkURL(true);
		setTitle('');
		setArtist('');
		setAlbum('');
		setGrouping('');
	};

	const onFileSwitchChange = (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
		if (checked) {
			setYouTubeURL('');
			setValidYouTubeURL(true);
			setFileType(FILE_TYPE.WAV_UPLOAD);
		} else {
			if (fileInputRef.current && fileInputRef.current.files) {
				fileInputRef.current.files = null;
				setFileName('');
			}
			setFileType(FILE_TYPE.YOUTUBE);
		}
		validateForm();
	};

	const onYouTubeURLChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const text = event.target.value.trim();
		const valid = RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(text);
		setValidYouTubeURL(valid);
		validateForm();
	};

	const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const files = event.target.files;
		if (files && files.length > 0) {
			const file = files[0];
			if (file.name.endsWith('.mp3')) {
				setFileType(FILE_TYPE.MP3_UPLOAD);
			} else if (file.name.endsWith('.wav')) {
				setFileType(FILE_TYPE.WAV_UPLOAD);
			}
			setFileName(file.name);
		}
		validateForm();
	};

	const onArtworkURLChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const text = event.target.value.trim();
		const valid = RegExp(/^https:\/\/(www\.)?(soundcloud\.com\/.+|.+\.(jpg|jpeg|png))/).test(text);
		setArtworkURL(text);
		setValidArtworkURL(valid);
	};

	const onBrowseClick = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
		if (fileInputRef.current) {
			fileInputRef.current.click();
		}
	};

	const defaultTextFieldProps: TextFieldProps = {
		sx: { mx: 3, flex: 1 },
		variant: 'standard',
	};

	const defaultContainerProps: ContainerProps = {
		sx: {
			flexDirection: 'row',
			display: 'flex',
			alignItems: 'center',
			my: 10,
		},
	};

	return (
		<Container>
			<Box sx={{ m: 1 }}>
				<Typography sx={{ my: 5 }} variant="h2">
					MP3 Downloader
				</Typography>
				<Divider variant="middle" />
				<Container {...defaultContainerProps}>
					<YouTube
						sx={{
							color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
						}}
					/>
					<TextField
						{...defaultTextFieldProps}
						value={youTubeURL}
						label="YouTube URL"
						disabled={fileType !== FILE_TYPE.YOUTUBE}
						onChange={onYouTubeURLChange}
						error={!validYouTubeURL}
						helperText={validYouTubeURL ? '' : 'Must be a valid YouTube link.'}
					/>
					<Switch onChange={onFileSwitchChange} value={fileType !== FILE_TYPE.YOUTUBE} />
					<TextField {...defaultTextFieldProps} value={fileName} label="File Upload" disabled />
					<input
						ref={fileInputRef}
						onChange={onFileChange}
						style={{ display: 'none' }}
						type="file"
						accept=".mp3,.wav"
					/>
					<Button
						variant="contained"
						disabled={fileType !== FILE_TYPE.MP3_UPLOAD || fileType !== FILE_TYPE.WAV_UPLOAD}
						onClick={onBrowseClick}
					>
						Browse
					</Button>
				</Container>
				<Container {...defaultContainerProps}>
					<TextField
						{...defaultTextFieldProps}
						label="Artwork URL"
						value={artworkURL}
						onChange={onArtworkURLChange}
						error={!validArtworkURL}
						helperText={validArtworkURL ? '' : 'Must be a valid Soundcloud or image link.'}
					/>
					<img
						style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }}
						src={artworkURL && validArtworkURL ? artworkURL : Image}
						alt="Cover Art"
					/>
				</Container>
				<Container {...defaultContainerProps}>
					<TextField
						label="Title"
						{...defaultTextFieldProps}
						value={title}
						onChange={(e) => setTitle(e.target.value)}
					/>
					<TextField
						label="Artist"
						{...defaultTextFieldProps}
						value={artist}
						onChange={(e) => setArtist(e.target.value)}
					/>
					<TextField
						label="Album"
						{...defaultTextFieldProps}
						value={album}
						onChange={(e) => setAlbum(e.target.value)}
					/>
					<TextField
						label="Grouping"
						{...defaultTextFieldProps}
						value={grouping}
						onChange={(e) => setGrouping(e.target.value)}
					/>
				</Container>
				<Container {...defaultContainerProps} sx={{ ...defaultContainerProps.sx, justifyContent: 'center' }}>
					<Button variant="contained" sx={{ mx: 2 }} disabled={!validForm}>
						{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
						{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
						{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
					</Button>
					<Button sx={{ mx: 2 }} variant="contained" onClick={reset}>
						Reset
					</Button>
				</Container>
			</Box>
		</Container>
	);
};

export default MP3Downloader;
