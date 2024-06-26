import { Box, Button, useTheme } from "@mui/material";
import { tokens } from "src/theme";
import Header from "src/components/Layouts/Header/Header";
import { mockDataChapters } from "src/data/mockData";
import ChapterCard from "src/components/chapters/ChapterCard";
import { useOutletContext, useParams } from "react-router-dom";
import React from "react";
import { useGetEpisodeChaptersListMutation, useGetEpisodesDetailMutation } from "src/services/api";

let sequences = []
function CreateSliderMarkersWithEpisodeSequences(sequences) {
    let total = sequences.length
    let divided = Math.floor(total/10)
    let nextPosition = 0
    return sequences.map((value, index)=>{
        let obj = {
            value: index,
            label: value.start_time
        }
        nextPosition += divided
        return obj
    })
}

const Chapters = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [loading, setLoading] = useOutletContext().loader

    const {episode_id} = useParams()
    
    
    const [episode, setEpisode] = React.useState(null)
    const [getEpisodeDetail] = useGetEpisodesDetailMutation()
    const getEpisodeDetailFunc = async ()=>{
        setLoading(true)
        const response = await getEpisodeDetail(episode_id)
        if (!!response.error) {
            let dataObject = response.error.data;
            console.log(dataObject.errors);
            SetApiErrors(dataObject.errors)
            
        } else {
            console.log("Login Success")
            let dataObject = response.data.data;
            // sequences = CreateSliderMarkersWithEpisodeSequences(dataObject.sequences)
            setEpisode(dataObject)
            await getChaptersfunc()
            // const {access_token} =  getToken()
            console.log(dataObject)
        }
        setLoading(false)
    }
    
    const [data, setData] = React.useState([])
    const [apiErrors, SetApiErrors] = React.useState({})
    const [getEpisodeChapters, {isLoading}] = useGetEpisodeChaptersListMutation()


    const getChaptersfunc = async ()=>{
        const response = await getEpisodeChapters(episode_id)
        if (!!response.error) {
            let dataObject = response.error.data;
            console.log(dataObject.errors);
            SetApiErrors(dataObject.errors)
            
        } else {
            let dataObject = response.data.data;
            setData(dataObject.results)
            console.log(dataObject)
        }
    }

    
    const [refreshNeeded, setRefreshNeeded] = React.useState(0)
    React.useEffect(()=>{
        window.scrollTo({behavior: "smooth", top: 0})
        getEpisodeDetailFunc()
    }, [refreshNeeded])

    return (
        <Box m="20px">
            <Header title="Chapter Selection" subtitle="List of all Chapters" />

            <Box sx={{ flexGrow: 1 }}>
                {/* {mockDataChapters.map(chapter => ( */}
                { episode != null && data.map((ch, index)=>
                    <ChapterCard 
                        key={ch.id+ch.start_sequence_number+ch.end_sequence_number}
                        episodeId={ch.episode_id}
                        chapterId={ch.id}
                        chapterTitle={ch.title} 
                        chapterMakerName={""} 
                        chapterTranscript={ch.content} 
                        episodeTranscript={episode.content}
                        startTime={ch.num_start_time}
                        endTime={ch.num_end_time}
                        src={"/images/benedwards.png"}
                        startSeq={ch.start_sequence_number}
                        endSeq={ch.end_sequence_number}
                        sequences={episode.sequences}
                        timeStamps={episode.sliderData}
                        min_step={episode.min_difference}
                        refresher={()=>setRefreshNeeded(refreshNeeded+1)}
                    />
                )}
            </Box>
        </Box>
    );
}

export default Chapters;