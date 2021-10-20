import React, { useState, useRef, useEffect } from 'react';
import {
	Box,
	Container,
	Divider,
	Typography,
	TextField,
	Switch,
	Button,
	TextFieldProps,
	Stack,
	CircularProgress,
} from '@mui/material';
import { YouTube } from '@mui/icons-material';
import Image from '../images/blank_image.jpeg';
import { FILE_TYPE } from '../utils/enums';
import { useDebounce } from '../utils/helpers';

const MusicDownloader = () => {
	const [validForm, setValidForm] = useState(false);

	const [fileType, setFileType] = useState(FILE_TYPE.YOUTUBE);

	const [youTubeURL, setYouTubeURL] = useState('');
	const debouncedYouTubeURL = useDebounce(youTubeURL, 500);
	const [fileName, setFileName] = useState('');
	const [validYouTubeURL, setValidYouTubeURL] = useState(false);

	const [fetchingArtwork, setFetchingArtwork] = useState(false);
	const [artworkURL, setArtworkURL] = useState('');
	const debouncedArtworkURL = useDebounce(artworkURL, 250);
	const [validArtworkURL, setValidArtworkURL] = useState(false);

	const [title, setTitle] = useState('');
	const [artist, setArtist] = useState('');
	const [album, setAlbum] = useState('');
	const [grouping, setGrouping] = useState('');

	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

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
			setValidYouTubeURL(false);
			setFileType(FILE_TYPE.WAV_UPLOAD);
		} else {
			if (fileInputRef.current && fileInputRef.current.files) {
				fileInputRef.current.files = null;
				setFileName('');
			}
			setFileType(FILE_TYPE.YOUTUBE);
		}
		setValidForm(false);
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
	};

	const onBrowseClick = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
		if (fileInputRef.current) {
			fileInputRef.current.click();
		}
	};

	const performOperation = async (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
		const formData = new FormData();
		formData.append('youtubeURL', youTubeURL);
		if (fileInputRef.current) {
			const files = fileInputRef.current.files;
			if (files && files.length > 0) {
				formData.append('file', files[0]);
			}
		}
		formData.append('artworkURL', artworkURL);
		formData.append('title', title);
		formData.append('artist', artist);
		formData.append('album', album);
		formData.append('grouping', grouping);
		const response = await fetch('/download', { method: 'POST', body: formData });
		if (response.status === 200) {
			// const file = await response.blob();
			// console.log(file);
		}
	};

	useEffect(() => {
		let valid = true;
		if (fileType === FILE_TYPE.YOUTUBE) {
			valid = validYouTubeURL && valid;
		} else if (fileType === FILE_TYPE.MP3_UPLOAD || fileType === FILE_TYPE.WAV_UPLOAD) {
			valid = fileName !== '' && valid;
		}
		valid = title !== '' && valid;
		valid = artist !== '' && valid;
		valid = album !== '' && valid;
		setValidForm(valid);
	}, [album, artist, fileName, fileType, title, validYouTubeURL]);

	useEffect(() => {
		const text = title;
		if (text) {
			let album = '';

			const openPar = text.indexOf('(');
			const closePar = text.indexOf(')');
			const specialTitle = (openPar !== -1 || closePar !== -1) && openPar < closePar;

			const songTitle = specialTitle ? text.substring(0, openPar).trim() : text.trim();
			album = songTitle;
			const songTitleWords = songTitle.split(' ');

			if (songTitleWords.length > 2) {
				album = songTitleWords.map((word) => word.charAt(0)).join('');
			}
			if (specialTitle) {
				const specialWords = text.substring(openPar + 1, closePar).split(' ');
				album = `${album} - ${specialWords[specialWords.length - 1]}`;
			} else {
				album = album ? `${album} - Single` : '';
			}
			setAlbum(album);
		}
	}, [title]);

	useEffect(() => {
		const valid = RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(youTubeURL);
		setValidYouTubeURL(valid);
	}, [youTubeURL]);

	useEffect(() => {
		const valid = RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(artworkURL);
		setValidArtworkURL(valid);
	}, [artworkURL]);

	useEffect(() => {
		const getGrouping = async (youTubeURL: string) => {
			if (youTubeURL) {
				const params = new URLSearchParams();
				params.append('youtubeURL', youTubeURL);
				const response = await fetch(`/grouping?${params}`);
				if (response.status === 200) {
					const json = await response.json();
					setGrouping(json.grouping);
				}
			}
		};
		getGrouping(debouncedYouTubeURL);
	}, [debouncedYouTubeURL]);

	useEffect(() => {
		const getArtwork = async (url: string) => {
			if (url && !validArtworkURL) {
				const params = new URLSearchParams();
				params.append('artworkURL', url);
				const response = await fetch(`/getArtwork?${params}`);
				if (response.status === 200) {
					const json = await response.json();
					if (json.artworkURL !== url) {
						setArtworkURL(json.artworkURL);
					}
				} else {
					setArtworkURL(url);
				}
			}
			setFetchingArtwork(false);
		};
		setFetchingArtwork(true);
		getArtwork(debouncedArtworkURL);
	}, [debouncedArtworkURL, validArtworkURL]);

	const defaultTextFieldProps: TextFieldProps = {
		sx: { mx: 3, flex: 1 },
		variant: 'standard',
	};

	return (
		<Container>
			<Box sx={{ my: 1 }}>
				<Typography sx={{ my: 5 }} variant="h2">
					MP3 Downloader / Convertor
				</Typography>
				<Divider variant="middle" />
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<YouTube
						sx={{
							color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
						}}
					/>
					<TextField
						{...defaultTextFieldProps}
						required
						value={youTubeURL}
						label="YouTube URL"
						disabled={fileType !== FILE_TYPE.YOUTUBE}
						onChange={(e) => setYouTubeURL(e.target.value)}
						error={youTubeURL !== '' && !validYouTubeURL}
						helperText={youTubeURL === '' || validYouTubeURL ? '' : 'Must be a valid YouTube link.'}
					/>
					<Switch onChange={onFileSwitchChange} value={fileType !== FILE_TYPE.YOUTUBE} />
					<TextField {...defaultTextFieldProps} value={fileName} label="File Upload" disabled required />
					<input
						ref={fileInputRef}
						onChange={onFileChange}
						style={{ display: 'none' }}
						type="file"
						accept=".mp3,.wav"
					/>
					<Button
						variant="contained"
						disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
						onClick={onBrowseClick}
					>
						Browse
					</Button>
				</Stack>
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<TextField
						{...defaultTextFieldProps}
						label="Artwork URL"
						value={artworkURL}
						onChange={(e) => setArtworkURL(e.target.value)}
						error={artworkURL !== '' && !validArtworkURL}
						helperText={
							artworkURL === '' || validArtworkURL
								? 'Supports soundcloud links to get cover art'
								: 'Must be a valid image link.'
						}
					/>
					{fetchingArtwork ? (
						<CircularProgress />
					) : (
						<img
							style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }}
							src={artworkURL && validArtworkURL ? artworkURL : Image}
							alt="Cover Art"
						/>
					)}
				</Stack>
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<TextField
						label="Title"
						required
						{...defaultTextFieldProps}
						value={title}
						onChange={(e) => setTitle(e.target.value)}
					/>
					<TextField
						label="Artist"
						required
						{...defaultTextFieldProps}
						value={artist}
						onChange={(e) => setArtist(e.target.value)}
					/>
					<TextField
						label="Album"
						required
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
				</Stack>
				<Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ my: 10 }}>
					<Button variant="contained" disabled={!validForm} onClick={performOperation}>
						{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
						{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
						{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
					</Button>
					<Button variant="contained" onClick={reset}>
						Reset
					</Button>
				</Stack>
			</Box>
		</Container>
	);
};

export default MusicDownloader;
